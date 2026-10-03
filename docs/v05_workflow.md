# v0.5 End-to-End Workflow

A v0.5 research run performs the following sequence:

1. Read AWID3-style input.
2. Normalize the selected 802.11 schema.
3. Run feature-name leakage checks.
4. Split into train / validation / test.
5. Train all configured research models.
6. Calculate validation probabilities.
7. Calibrate a decision threshold on validation only.
8. Freeze the threshold.
9. Evaluate calibrated predictions on test.
10. Measure false positives and false negatives.
11. Apply the explicit model-promotion policy.
12. Save each model artifact.
13. Register each candidate locally with a version and SHA-256 digest.
14. Select the best validation candidate.
15. Promote it to `champion` only if policy checks pass.
16. Compute permutation importance.
17. Optionally compute SHAP for the tree model.
18. Optionally log/register the selected model in MLflow.
19. Generate JSON and Markdown reports.

The final test split is never used to select the threshold.
