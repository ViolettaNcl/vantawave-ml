from vantawave.lab.evidence import build_evidence_bundle

def test_evidence_bundle_hashes_files(tmp_path):
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("abc", encoding="utf-8")
    bundle = build_evidence_bundle(
        session_id="s1",
        target_id="t1",
        files={"note": evidence},
        output=tmp_path / "bundle.json",
    )
    assert len(bundle.items) == 1
    assert len(bundle.items[0].sha256) == 64
    assert (tmp_path / "bundle.json").exists()
