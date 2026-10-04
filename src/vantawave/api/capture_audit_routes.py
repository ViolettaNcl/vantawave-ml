from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field, SecretStr

from vantawave.capture_audit.aircrack import capability as aircrack_capability
from vantawave.capture_audit.aircrack import verify_single_candidate
from vantawave.capture_audit.analyzer import (
    CaptureAuditUnavailable,
    analyze_capture,
)
from vantawave.capture_audit.store import CaptureAuditStore
from vantawave.capture_audit.vault import vault
from vantawave.core.settings import load_settings
from vantawave.lab.registry import AuthorizedTargetRegistry
from vantawave.wifi_recovery.windows import connect_with_password


router = APIRouter(prefix="/capture-audit", tags=["Authorized Capture Audit"])
store = CaptureAuditStore()
MAX_UPLOAD_BYTES = 200 * 1024 * 1024


def _require_local(request: Request):
    if request.client is None or request.client.host not in {"127.0.0.1", "::1", "testclient"}:
        raise HTTPException(
            status_code=403,
            detail="Capture Audit write/secret actions are restricted to localhost.",
        )


def _authorized_target(target_id: str) -> dict:
    try:
        return AuthorizedTargetRegistry().require_authorized(target_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Authorized target not found.") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


class CandidateRequest(BaseModel):
    audit_id: str = Field(min_length=1, max_length=64)
    candidate: SecretStr
    security: str = "WPA2-Personal"


class TokenConnectRequest(BaseModel):
    token: str = Field(min_length=10, max_length=128)


@router.get("/capabilities")
def capabilities():
    air = aircrack_capability()
    return {
        "offline_capture_analysis": True,
        "authorized_target_required": True,
        "eapol_detection": True,
        "single_candidate_verification": air.available,
        "aircrack_ng": air.to_dict(),
        "wordlist_cracking_api": False,
        "bruteforce_api": False,
        "ssid_only_password_recovery": False,
        "ephemeral_verified_secret": True,
    }


@router.post("/upload")
async def upload_capture(
    request: Request,
    target_id: str = Form(...),
    capture: UploadFile = File(...),
):
    _require_local(request)
    target = _authorized_target(target_id)

    suffix = Path(capture.filename or "").suffix.lower()
    if suffix not in {".pcap", ".pcapng", ".cap"}:
        raise HTTPException(
            status_code=400,
            detail="Supported capture extensions: .pcap, .pcapng, .cap",
        )

    audit_id = store.create_id()
    destination = store.capture_path(audit_id, suffix)

    total = 0
    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await capture.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Capture exceeds 200 MB local audit limit.",
                    )
                handle.write(chunk)

        result = analyze_capture(destination, target=target)
        payload = {
            "audit_id": audit_id,
            "target": {
                "target_id": target["target_id"],
                "name": target["name"],
                "ssid": target["ssid"],
                "bssid": target["bssid"],
            },
            "capture": result.to_dict(),
        }
        store.save_report(audit_id, payload)
        return payload
    except HTTPException:
        store.delete(audit_id)
        raise
    except (CaptureAuditUnavailable, RuntimeError, FileNotFoundError) as exc:
        store.delete(audit_id)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        await capture.close()


@router.get("/{audit_id}")
def audit_report(audit_id: str, request: Request):
    _require_local(request)
    try:
        return store.load_report(audit_id)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Capture audit not found.") from exc


@router.post("/verify-candidate")
def verify_candidate(payload: CandidateRequest, request: Request):
    _require_local(request)

    try:
        report = store.load_report(payload.audit_id)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Capture audit not found.") from exc

    target = _authorized_target(report["target"]["target_id"])
    capture_report = report["capture"]

    if not capture_report.get("target_seen"):
        raise HTTPException(
            status_code=400,
            detail="The authorized target was not observed in this capture.",
        )
    if not capture_report.get("candidate_verification_ready"):
        raise HTTPException(
            status_code=400,
            detail="The capture does not contain enough matching EAPOL evidence to attempt candidate verification.",
        )

    if payload.security != "WPA2-Personal":
        raise HTTPException(
            status_code=400,
            detail="The Aircrack-ng single-candidate adapter currently supports WPA/WPA2-PSK capture verification, not WPA3-SAE.",
        )

    candidate = payload.candidate.get_secret_value()
    if "\n" in candidate or "\r" in candidate:
        raise HTTPException(
            status_code=400,
            detail="Candidate must be a single passphrase, not a multi-line wordlist.",
        )
    if not 8 <= len(candidate) <= 63:
        raise HTTPException(
            status_code=400,
            detail="A WPA2-Personal passphrase candidate must contain 8–63 characters.",
        )

    try:
        result = verify_single_candidate(
            capture_path=capture_report["path"],
            ssid=target["ssid"],
            bssid=target["bssid"],
            candidate=candidate,
        )
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    response = result.to_dict()
    response.update(
        {
            "audit_id": payload.audit_id,
            "ssid": target["ssid"],
            "masked_secret": None,
            "secret_token": None,
        }
    )

    if result.verified:
        token = vault.put(
            secret=candidate,
            ssid=target["ssid"],
            security=payload.security,
        )
        response["secret_token"] = token
        response["masked_secret"] = vault.masked(token)

    return response


@router.post("/connect-verified")
def connect_verified(payload: TokenConnectRequest, request: Request):
    _require_local(request)
    try:
        item = vault.get(payload.token)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Verified secret token is missing or expired.",
        ) from exc

    try:
        return connect_with_password(
            item.ssid,
            item.secret,
            security=item.security,
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/secret/{token}")
def reveal_verified_secret(token: str, request: Request):
    _require_local(request)
    settings = load_settings()
    if not settings.allow_local_credential_view:
        raise HTTPException(
            status_code=403,
            detail=(
                "Local secret viewing is disabled. Set "
                "VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true before startup."
            ),
        )
    try:
        item = vault.get(token)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Verified secret token is missing or expired.",
        ) from exc
    return {
        "ssid": item.ssid,
        "password": item.secret,
        "message": "Ephemeral verified candidate returned locally.",
    }


@router.delete("/{audit_id}")
def delete_audit(audit_id: str, request: Request):
    _require_local(request)
    try:
        store.delete(audit_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"deleted": True, "audit_id": audit_id}
