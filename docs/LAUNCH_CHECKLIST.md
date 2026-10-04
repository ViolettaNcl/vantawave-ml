# VantaWave ML — GitHub Launch Checklist

This checklist turns the repository from a portfolio artifact into a discoverable open-source project.

## 1. Repository metadata

Set the GitHub **About** description to:

> ML-powered Wi-Fi security research platform for anomaly detection, MLOps, adversary simulation and evidence-grounded SOC analysis.

Set the website after GitHub Pages is enabled:

`https://violettancl.github.io/vantawave-ml/`

Add these GitHub topics:

```text
wifi-security
wireless-security
cybersecurity
machine-learning
intrusion-detection
anomaly-detection
network-security
security-research
threat-detection
mlops
pytorch
fastapi
deep-learning
rag
shap
soc
red-team
blue-team
docker
python
```

## 2. GitHub Pages live demo

The repository already contains a read-only static demo at `docs/index.html`.

GitHub UI:

1. Repository → **Settings** → **Pages**.
2. Source: **Deploy from a branch**.
3. Branch: `main`.
4. Folder: `/docs`.
5. Save.

The site should appear at:

`https://violettancl.github.io/vantawave-ml/`

Then set that URL as the repository Website.

## 3. Social preview

Upload `docs/assets/social-preview.png` in:

**Settings → General → Social preview → Edit**.

The asset is already 1280×640.

## 4. License

`LICENSE` contains Apache-2.0. GitHub should detect it after the next push.

## 5. Release

Create a GitHub Release:

- Tag: `v1.1.1`
- Title: `VantaWave ML v1.1.1 — Launch Ready`
- Target: `main`
- Body: copy `docs/RELEASE_BODY_v1.1.1.md`
- Attach the source ZIP and wheel if desired.

## 6. Discussions

Enable **Settings → General → Features → Discussions**.

Recommended first discussion:

> **What should VantaWave benchmark next?**
>
> I am looking for feedback on Wi-Fi security datasets, anomaly-detection evaluation, and useful SOC workflows. The project deliberately separates synthetic demos from real benchmark claims.

## 7. Community issues

Create the issues prepared in `docs/COMMUNITY_ISSUES.md`.

Do not create fake activity. These should be real contribution opportunities.

## 8. CI gate

Do not launch publicly until the `CI` badge is green on `main`.

The v1.1.1 release pins Ruff and uses an explicit correctness-focused lint policy so CI behavior is reproducible across Ruff releases.

## 9. Launch channels

Use the drafts in `docs/LAUNCH_POSTS.md`.

Recommended order:

1. LinkedIn
2. r/MachineLearning or a suitable ML/security community following its self-promotion rules
3. DEV Community / Medium technical article
4. Hacker News Show HN
5. relevant curated awesome lists after the first real external benchmark

## 10. What to measure

Track weekly:

- GitHub stars
- unique visitors / clones in GitHub Insights
- forks
- issues/discussions
- external referrers
- demo visits
- contributions

Do not optimize only for stars. The best signal is whether engineers clone, run, discuss, or contribute.
