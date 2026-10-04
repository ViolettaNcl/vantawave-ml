# Authorized Capture Audit

## Purpose

This module follows the real WPA/WPA2 audit model used by tools such as
Aircrack-ng:

1. collect an authorized capture;
2. identify authentication evidence;
3. verify candidate passphrases against that evidence.

It does not claim that an SSID contains or reveals its password.

## Safety boundary

A capture audit requires an existing VantaWave `AuthorizedTarget`.

The target contains:

- target ID;
- SSID;
- BSSID;
- explicit authorization confirmation.

The uploaded capture is checked against that target.

The VantaWave API exposes only **single-candidate verification**.

It does not expose:

- wordlist cracking;
- brute-force cracking;
- packet injection;
- deauthentication;
- third-party target selection.

## Dependencies

Install Scapy support:

```powershell
python -m pip install -e ".[pcap]"
```

Install Aircrack-ng separately.

VantaWave discovers:

```text
aircrack-ng
aircrack-ng.exe
```

from `PATH`.

Alternatively:

```powershell
$env:VANTAWAVE_AIRCRACK_PATH="C:\Tools\aircrack-ng\aircrack-ng.exe"
```

## Dashboard

Open:

```text
http://127.0.0.1:8000/dashboard
```

Select **Capture Audit**.

### Step 1 — target and capture

Choose an already registered Authorized Lab target.

Upload:

- `.pcap`
- `.pcapng`
- `.cap`

VantaWave reports:

- SHA-256;
- total packets;
- 802.11 packets;
- target-related packets;
- EAPOL packets;
- target EAPOL packets;
- observed SSIDs/BSSIDs/clients;
- whether the target appears in the capture;
- whether candidate verification is potentially usable.

The EAPOL count is an evidence heuristic. Aircrack-ng ultimately determines
whether the capture contains usable WPA/WPA2 material.

### Step 2 — verify one candidate

Enter exactly one WPA2-Personal passphrase candidate.

VantaWave writes that candidate into a temporary one-line file, invokes
Aircrack-ng against the authorized capture and target, captures the result in
memory, then deletes the temporary file.

The candidate is not:

- stored in the capture report;
- stored in the database;
- added to MLflow;
- added to structured logs.

## Masked verified secret

If the candidate matches, VantaWave creates a short-lived in-memory token.

The dashboard displays:

```text
••••••••••••
```

Those characters are only a visual mask.

`Connect verified` retrieves the actual candidate from the in-memory vault and
asks Windows to connect to the target SSID.

The secret expires from the process vault automatically.

## Copy verified secret

For extra protection, returning the actual verified secret to browser
JavaScript is disabled unless:

```powershell
$env:VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW="true"
```

and the request originates from localhost.

This lets the dashboard copy the actual verified candidate while continuing to
display only a mask.

## WPA3

The Windows Recovery module can create WPA3-Personal connection profiles using
an owner-supplied password.

The Aircrack-ng capture verification adapter in v1.0.2 is restricted to the
WPA/WPA2-PSK style workflow and is not presented as WPA3-SAE password recovery.

## What this does not solve

If you only know:

```text
SSID = MyHomeWiFi
```

and have no saved credential, no router-management recovery path, no suitable
authentication evidence, and no correct password candidate, the module cannot
produce the unknown WPA2/WPA3 password.

A masked field cannot contain a secret the program does not possess.
