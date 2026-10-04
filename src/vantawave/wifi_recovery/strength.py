from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import re


COMMON_PATTERNS = (
    "password",
    "qwerty",
    "12345678",
    "internet",
    "wifi",
    "admin",
    "letmein",
)


@dataclass(frozen=True)
class PasswordAudit:
    score: int
    rating: str
    estimated_entropy_bits: float
    findings: list[str]

    def to_dict(self):
        return asdict(self)


def audit_password_strength(password: str) -> PasswordAudit:
    if not password:
        return PasswordAudit(
            score=0,
            rating="empty",
            estimated_entropy_bits=0.0,
            findings=["Password is empty."],
        )

    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"\d", password):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", password):
        pool += 32

    entropy = len(password) * math.log2(max(pool, 1))
    score = 0
    findings = []

    if len(password) >= 16:
        score += 45
    elif len(password) >= 12:
        score += 35
    elif len(password) >= 10:
        score += 25
    elif len(password) >= 8:
        score += 15
    else:
        findings.append("Use at least 12 characters for a stronger home Wi-Fi passphrase.")

    categories = sum(
        bool(re.search(pattern, password))
        for pattern in (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]")
    )
    score += categories * 10

    lowered = password.lower()
    if any(pattern in lowered for pattern in COMMON_PATTERNS):
        score -= 30
        findings.append("Password contains a common or predictable pattern.")

    if len(set(password)) <= max(3, len(password) // 4):
        score -= 20
        findings.append("Password repeats too few distinct characters.")

    if re.search(r"(.)\1\1", password):
        score -= 10
        findings.append("Password contains repeated character runs.")

    score = max(0, min(100, score))

    if score >= 80:
        rating = "strong"
    elif score >= 60:
        rating = "good"
    elif score >= 40:
        rating = "weak"
    else:
        rating = "very_weak"

    if not findings and rating in {"strong", "good"}:
        findings.append("No obvious local strength issues detected.")

    return PasswordAudit(
        score=score,
        rating=rating,
        estimated_entropy_bits=float(entropy),
        findings=findings,
    )
