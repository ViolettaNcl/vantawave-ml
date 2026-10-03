# Passive Sensor Architecture

## Goals

The v0.7 sensor layer separates **collection** from **ML**.

```text
Sensor Adapter
    ↓
WirelessEvent
    ↓
Event Store
    ↓
Rolling Window
    ↓
WindowFeatures
    ↓
Later ML / Incident Engine
```

This prevents hardware-specific code from being embedded inside model logic.

## Windows adapter

`WindowsNetshSensor` executes:

```text
netsh wlan show networks mode=bssid
```

It extracts OS-visible:

- SSID;
- BSSID;
- authentication/encryption;
- signal quality;
- radio type;
- channel.

This is not monitor-mode raw frame capture.

## Signal quality

Windows exposes a percentage in this interface. VantaWave also supplies an
estimated dBm value using:

```text
estimated dBm = signal_percent / 2 - 100
```

This is explicitly marked `rssi_estimated=true` and must not be treated as a
calibrated radio measurement.

## PCAP replay

Optional Scapy support reads offline PCAP/PCAPNG files and maps 802.11 frames
into normalized VantaWave events.

Supported normalized event categories:

- beacon;
- authentication;
- association/reassociation;
- deauthentication;
- disassociation;
- data;
- other 802.11.

No live sniffing or packet transmission is performed by the v0.7 PCAP adapter.

## Provenance

Every event records `source` and `collection_mode`.

This matters because OS discovery, offline raw-frame replay and future
authorized monitor-mode capture have different data quality and semantics.
