from __future__ import annotations

import re
from dataclasses import dataclass


CITATION_RE = re.compile(r"\[[A-Za-z0-9_.:-]+\]")


@dataclass(frozen=True)
class GroundingValidation:
    valid: bool
    citations_found: tuple[str, ...]
    invalid_citations: tuple[str, ...]
    reason: str | None = None


def validate_response_citations(
    text: str,
    *,
    allowed_citations: tuple[str, ...] | list[str],
) -> GroundingValidation:
    found = tuple(dict.fromkeys(CITATION_RE.findall(text)))
    allowed = set(allowed_citations)
    invalid = tuple(value for value in found if value not in allowed)

    if invalid:
        return GroundingValidation(
            valid=False,
            citations_found=found,
            invalid_citations=invalid,
            reason="Response contains citations that were not supplied as evidence.",
        )

    return GroundingValidation(
        valid=True,
        citations_found=found,
        invalid_citations=(),
        reason=None,
    )
