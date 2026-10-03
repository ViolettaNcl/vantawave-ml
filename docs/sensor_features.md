# Sensor Feature Windows

VantaWave aggregates normalized events into time windows.

Current output:

- `event_rate`
- `auth_rate`
- `assoc_rate`
- `deauth_rate`
- `disassoc_rate`
- `beacon_rate`
- `data_rate`
- `ap_observation_rate`
- `unique_bssids`
- `unique_transmitters`
- `unique_ssids`
- `rssi_mean`
- `rssi_std`
- `signal_percent_mean`
- `retry_ratio`
- `channel_count`

## Compatibility projection

`WindowFeatures.to_legacy_feature_row()` can project a window into the original
10-feature ML schema.

This exists for controlled experiments only.

Do not claim that a model trained on synthetic or differently collected
features is valid on live sensor windows until a real domain-matched training
and evaluation pipeline has been completed.
