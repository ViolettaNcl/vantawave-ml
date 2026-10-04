from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os
import shutil
import subprocess
import tempfile


@dataclass(frozen=True)
class AircrackCapability:
    available: bool
    executable: str | None
    reason: str | None

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class CandidateVerification:
    verified: bool
    usable_capture: bool
    tool: str
    message: str

    def to_dict(self):
        return asdict(self)


def capability() -> AircrackCapability:
    configured = os.getenv("VANTAWAVE_AIRCRACK_PATH")
    executable = None

    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.exists() and configured_path.is_file():
            executable = str(configured_path)

    if executable is None:
        executable = shutil.which("aircrack-ng") or shutil.which("aircrack-ng.exe")

    return AircrackCapability(
        available=executable is not None,
        executable=executable,
        reason=(
            None
            if executable
            else (
                "aircrack-ng was not found. Put it in PATH or set "
                "VANTAWAVE_AIRCRACK_PATH to the local executable."
            )
        ),
    )


def parse_aircrack_result(output: str) -> CandidateVerification:
    normalized = output.upper()
    if "KEY FOUND!" in normalized:
        return CandidateVerification(
            verified=True,
            usable_capture=True,
            tool="aircrack-ng",
            message="The supplied candidate matches the capture evidence.",
        )

    unusable_markers = (
        "NO VALID WPA HANDSHAKES FOUND",
        "NO EAPOL DATA WAS FOUND",
        "NO MATCHING NETWORK",
    )
    if any(marker in normalized for marker in unusable_markers):
        return CandidateVerification(
            verified=False,
            usable_capture=False,
            tool="aircrack-ng",
            message="Aircrack-ng could not find usable matching authentication evidence.",
        )

    return CandidateVerification(
        verified=False,
        usable_capture=True,
        tool="aircrack-ng",
        message="The supplied candidate was not verified by the capture.",
    )


def verify_single_candidate(
    *,
    capture_path: str | Path,
    ssid: str,
    bssid: str,
    candidate: str,
    timeout_seconds: int = 30,
) -> CandidateVerification:
    cap = capability()
    if not cap.available or cap.executable is None:
        raise RuntimeError(cap.reason or "aircrack-ng unavailable.")

    capture_path = Path(capture_path)
    if not capture_path.exists():
        raise FileNotFoundError(capture_path)
    if not candidate:
        raise ValueError("Candidate cannot be empty.")

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        prefix="vantawave-candidate-",
        suffix=".txt",
    ) as handle:
        handle.write(candidate)
        handle.write("\n")
        candidate_file = Path(handle.name)

    try:
        process = subprocess.run(
            [
                cap.executable,
                "-w",
                str(candidate_file),
                "-b",
                bssid,
                "-e",
                ssid,
                str(capture_path),
            ],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
        output = (process.stdout or "") + "\n" + (process.stderr or "")
        return parse_aircrack_result(output)
    finally:
        candidate_file.unlink(missing_ok=True)
