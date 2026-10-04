from __future__ import annotations

import platform

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, SecretStr

from vantawave.core.settings import load_settings
from vantawave.wifi_recovery.recovery import recovery_options
from vantawave.wifi_recovery.strength import audit_password_strength
from vantawave.wifi_recovery.windows import (
    WiFiRecoveryUnavailable,
    connect_with_password,
    current_wifi,
    delete_saved_profile,
    export_saved_key,
    gateway_info,
    list_saved_profiles,
    nearby_networks,
    profile_exists,
)


router = APIRouter(prefix="/wifi-recovery", tags=["Wi-Fi Recovery"])


def _loopback(request: Request) -> bool:
    if request.client is None:
        return False
    return request.client.host in {"127.0.0.1", "::1", "testclient"}


def _require_local(request: Request):
    if not _loopback(request):
        raise HTTPException(
            status_code=403,
            detail="This Wi-Fi recovery action is restricted to the local machine.",
        )


class SavedKeyRequest(BaseModel):
    ssid: str = Field(min_length=1, max_length=128)
    explicit_confirmation: bool = False


class PasswordAuditRequest(BaseModel):
    password: SecretStr


class ConnectRequest(BaseModel):
    ssid: str = Field(min_length=1, max_length=128)
    password: SecretStr
    security: str = "WPA2-Personal"


@router.get("/capabilities")
def capabilities():
    settings = load_settings()
    return {
        "windows": platform.system().lower() == "windows",
        "list_saved_profiles": True,
        "local_saved_key_export": True,
        "saved_key_view_enabled": settings.allow_local_credential_view,
        "nearby_network_scan": True,
        "connect_with_supplied_password": True,
        "delete_saved_profile": True,
        "password_strength_audit": True,
        "unknown_wpa2_wpa3_password_recovery": False,
        "note": (
            "If this PC has never connected to an SSID, Windows has no saved key "
            "for VantaWave to reveal. Unknown WPA2/WPA3 keys are not derived by this module."
        ),
    }


@router.get("/profiles")
def profiles():
    try:
        return {"profiles": [item.to_dict() for item in list_saved_profiles()]}
    except WiFiRecoveryUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/nearby")
def nearby():
    try:
        return {"networks": nearby_networks()}
    except (WiFiRecoveryUnavailable, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/current")
def current():
    try:
        return current_wifi().to_dict()
    except (WiFiRecoveryUnavailable, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/gateways")
def gateways():
    try:
        return {"gateways": [item.to_dict() for item in gateway_info()]}
    except WiFiRecoveryUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/status")
def status(ssid: str = Query(min_length=1, max_length=128)):
    try:
        saved = profile_exists(ssid)
        gateways = gateway_info()
    except WiFiRecoveryUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "ssid": ssid,
        "saved_profile": saved,
        "stored_key_available": saved,
        "unknown_password_derivable": False,
        "recovery_options": recovery_options(
            saved_profile_exists=saved,
            gateway_available=bool(gateways),
        ),
        "gateways": [item.to_dict() for item in gateways],
    }


@router.post("/saved-key")
def saved_key(payload: SavedKeyRequest, request: Request):
    _require_local(request)
    settings = load_settings()
    if not settings.allow_local_credential_view:
        raise HTTPException(
            status_code=403,
            detail=(
                "Saved-key viewing is disabled. Set "
                "VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true locally to enable it."
            ),
        )
    if not payload.explicit_confirmation:
        raise HTTPException(
            status_code=400,
            detail="explicit_confirmation=true is required.",
        )

    try:
        key = export_saved_key(payload.ssid, allow_secret=True)
    except (WiFiRecoveryUnavailable, RuntimeError, PermissionError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if key is None:
        return {
            "ssid": payload.ssid,
            "saved": False,
            "password": None,
            "message": "No stored key exists for this SSID on this Windows PC.",
        }

    return {
        "ssid": payload.ssid,
        "saved": True,
        "password": key,
        "message": "Stored Windows Wi-Fi key returned locally.",
    }


@router.post("/password-strength")
def password_strength(payload: PasswordAuditRequest, request: Request):
    _require_local(request)
    return audit_password_strength(payload.password.get_secret_value()).to_dict()


@router.post("/connect")
def connect(payload: ConnectRequest, request: Request):
    _require_local(request)
    try:
        return connect_with_password(
            payload.ssid,
            payload.password.get_secret_value(),
            security=payload.security,
        )
    except (WiFiRecoveryUnavailable, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/profiles/{ssid}")
def delete_profile(ssid: str, request: Request):
    _require_local(request)
    try:
        return delete_saved_profile(ssid)
    except WiFiRecoveryUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
