from pathlib import Path

from vantawave.release.validation import validate_release


def test_release_validation_passes_for_repository_root():
    root = Path(__file__).resolve().parents[1]
    checks = validate_release(root)
    failed = [item for item in checks if not item.ok]
    assert not failed, [item.to_dict() for item in failed]
