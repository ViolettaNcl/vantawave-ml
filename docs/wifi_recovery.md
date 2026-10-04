# Wi-Fi Recovery & Authorized Audit

VantaWave v1.0.1 adds a Windows-focused Wi-Fi recovery assistant.

## What it can do

- list Windows-saved Wi-Fi profiles;
- scan OS-visible nearby Wi-Fi networks;
- inspect the current Wi-Fi interface;
- identify possible default gateways;
- reveal a locally saved Wi-Fi key only after explicit local enablement;
- locally audit a password supplied by the operator;
- create a Windows Wi-Fi profile from a supplied WPA2/WPA3 passphrase;
- request a connection through Windows;
- remove the saved Windows profile again.

## What it cannot do

If the laptop has **never connected to an SSID**, Windows has no saved key for
that SSID.

VantaWave does not derive an unknown WPA2/WPA3 password from nearby radio
traffic. The dashboard explicitly reports:

```text
unknown_wpa2_wpa3_password_recovery: false
```

This is not a hidden or unfinished feature.

## Why saved-key viewing is restricted

The dashboard does not expose saved Wi-Fi keys by default.

To enable local saved-key viewing:

```powershell
$env:VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW="true"
python -m uvicorn vantawave.api.main:app --reload
```

The endpoint additionally requires that the request originates from the local
machine.

This prevents a VantaWave instance bound to a LAN interface from becoming a
remote credential-disclosure service.

## Dashboard workflow

Open:

```text
http://127.0.0.1:8000/dashboard
```

Select **Wi-Fi Recovery**.

Recommended flow:

1. Scan nearby networks.
2. Choose your SSID.
3. Check recovery status.
4. VantaWave reports whether Windows already has a saved profile.
5. Review legitimate router recovery paths if no profile exists.
6. If you already know the passphrase, enter it locally and select the matching
   WPA2/WPA3 Personal mode.
7. Audit password strength if desired.
8. Click **Connect**.
9. Remove the Windows profile later if you want to return the laptop to a
   no-saved-profile state.

## CLI

List profiles:

```powershell
python scripts/wifi_recovery.py profiles
```

Scan:

```powershell
python scripts/wifi_recovery.py scan
```

Check an SSID:

```powershell
python scripts/wifi_recovery.py status --ssid "MyWiFi"
```

Show a key that Windows has already saved:

```powershell
python scripts/wifi_recovery.py saved-key --ssid "MyWiFi" --confirm
```

Connect using a passphrase you supply interactively:

```powershell
python scripts/wifi_recovery.py connect --ssid "MyWiFi" --security WPA2-Personal
```

The password prompt does not echo the password.

Remove the saved profile:

```powershell
python scripts/wifi_recovery.py delete-profile --ssid "MyWiFi"
```

Local strength audit:

```powershell
python scripts/wifi_recovery.py audit-password
```

## Router recovery

When a default gateway is visible, VantaWave can show it as a possible router
management address.

This only helps locate an authorized router-management surface. It does not
bypass router admin authentication.

If there is no saved Windows key, legitimate recovery options normally include:

- router label / installation card;
- official router or ISP app;
- authorized router administration;
- factory reset and reconfiguration as a last resort.

## Credential handling

Passwords submitted to the connect/strength endpoints use secret request
fields and are not included in VantaWave response payloads, reports, registry
metadata or structured logging.

The Windows Wi-Fi profile created for a successful connection is managed by
Windows and may remain saved until explicitly removed.
