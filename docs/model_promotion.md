# Model Promotion

VantaWave ML does not promote a model merely because it is the newest model.

Default promotion policy:

- test F1 >= 0.80;
- test PR-AUC >= 0.85;
- test false-positive rate <= 0.10;
- validation/test F1 gap <= 0.10.

Every failed check is written to the report.

If the selected candidate passes, the local registry assigns it the
`champion` alias and archives the previous champion.

These numbers are engineering defaults for the portfolio project, not universal
security thresholds. They should be revisited after evaluation on real data.
