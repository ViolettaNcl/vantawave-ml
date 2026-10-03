# Error Analysis

Aggregate metrics are insufficient for security systems.

v0.5 explicitly tracks:

- false-positive count;
- false-negative count;
- correct predictions;
- highest-confidence false positives;
- lowest-score false negatives.

The calibrated threshold is used for the analysis.

This layer is intended to answer questions such as:

- What normal traffic is repeatedly being flagged?
- Which attacks are being missed?
- Are errors clustered near the decision threshold?
- Does a new feature reduce false alarms or simply improve average accuracy?

Later releases can attach original packet/session identifiers to these cases.
