FEATURE_COLUMNS = [
    "auth_rate", "assoc_rate", "deauth_rate", "beacon_rate",
    "unique_clients", "unique_bssids", "rssi_mean", "rssi_std",
    "retry_ratio", "event_rate",
]
TARGET_COLUMN = "is_anomaly"
OPTIONAL_COLUMNS = ["timestamp", "session_id", "source"]

NON_NEGATIVE_FEATURES = {
    "auth_rate", "assoc_rate", "deauth_rate", "beacon_rate",
    "unique_clients", "unique_bssids", "rssi_std", "retry_ratio", "event_rate",
}
BOUNDED_FEATURES = {"retry_ratio": (0.0, 1.0)}
