from vantawave.capture_audit.aircrack import parse_aircrack_result
from vantawave.capture_audit.store import CaptureAuditStore
from vantawave.capture_audit.vault import EphemeralSecretVault


def test_aircrack_result_parser():
    found = parse_aircrack_result("KEY FOUND! [ correctpass ]")
    assert found.verified is True
    assert found.usable_capture is True

    unusable = parse_aircrack_result("No valid WPA handshakes found.")
    assert unusable.verified is False
    assert unusable.usable_capture is False

    wrong = parse_aircrack_result("Passphrase not in dictionary")
    assert wrong.verified is False
    assert wrong.usable_capture is True


def test_capture_store_roundtrip(tmp_path):
    store = CaptureAuditStore(tmp_path)
    audit_id = store.create_id()
    path = store.capture_path(audit_id, ".pcap")
    path.write_bytes(b"pcap-placeholder")
    report = {
        "audit_id": audit_id,
        "target": {"target_id": "t1"},
        "capture": {"path": str(path)},
    }
    store.save_report(audit_id, report)
    assert store.load_report(audit_id)["audit_id"] == audit_id
    store.delete(audit_id)
    assert not store.audit_dir(audit_id).exists()


def test_ephemeral_secret_vault_masks_but_keeps_real_value():
    vault = EphemeralSecretVault(ttl_minutes=10)
    token = vault.put(
        secret="CorrectPass123!",
        ssid="Lab",
        security="WPA2-Personal",
    )
    masked = vault.masked(token)
    assert set(masked) == {"•"}
    assert "CorrectPass123!" not in masked
    assert vault.get(token).secret == "CorrectPass123!"
