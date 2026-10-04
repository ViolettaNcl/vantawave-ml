# Security Policy

VantaWave ML is intended for defensive research and authorized laboratory use.

Do not commit:
- real Wi-Fi passwords;
- private keys;
- credentials;
- personally sensitive packet captures;
- private production telemetry.

Active laboratory experiments must be restricted to equipment you own or are
explicitly authorized to test.

If a security issue is found in VantaWave ML itself, report it privately before
publishing exploit details.


## Local Wi-Fi credentials

VantaWave does not expose saved Wi-Fi keys over the network by default.

Saved-key viewing requires:

1. `VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true`;
2. a request originating from the local machine;
3. explicit confirmation in the request.

Passwords supplied to the connect/strength endpoints are not returned in API
responses and are not persisted in VantaWave artifacts/logs.

Do not enable local credential viewing on an instance intentionally exposed to
untrusted local users.

The Wi-Fi Recovery module does not implement unknown WPA2/WPA3 password
derivation or generic third-party credential recovery.


## Authorized capture candidate verification

Capture Audit is localhost-oriented and requires an explicitly authorized
VantaWave Lab target.

The application intentionally exposes no wordlist/brute-force HTTP API.

Candidate verification accepts exactly one passphrase per request. Newlines
are rejected to prevent treating a request as a wordlist.

Verified candidates are stored only in a short-lived process-memory vault and
are not written to reports, database rows, MLflow artifacts or structured logs.

Actual secret retrieval requires both localhost and
`VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true`.
