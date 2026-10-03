# AWID3 Research Adapter

VantaWave ML v0.4 introduces a research adapter for AWID3-style CSV exports.

## Dataset

AWID3 is a wireless intrusion-detection dataset created by the University of
the Aegean for modern IEEE 802.11 enterprise environments. It is distributed
as PCAP and CSV data and includes normal traffic plus multiple attack
scenarios.

Official dataset page:

https://icsdweb.aegean.gr/awid/

The dataset is intentionally **not bundled** in this repository. Follow the
dataset owner's access and licensing terms, obtain the CSV files yourself,
then place local research files under a non-committed data directory.

## Feature profile

The v0.4 adapter uses a compact 16-feature IEEE 802.11 set used in AWID
research:

- frame.len
- radiotap.length
- radiotap.dbm_antsignal
- wlan.duration
- radiotap.present.tsft
- radiotap.channel.freq
- radiotap.channel.type.cck
- radiotap.channel.type.ofdm
- wlan.fc.type
- wlan.fc.subtype
- wlan.fc.ds
- wlan.fc.frag
- wlan.fc.retry
- wlan.fc.pwrmgt
- wlan.fc.moredata
- wlan.fc.protected

VantaWave supports common column aliases such as `radiotap.len`.

## Current task

v0.4 performs **binary classification**:

- normal → 0
- any non-normal AWID3 label → 1

Raw attack labels are retained in memory for analysis. Multi-class modeling is
a later step.

## Preprocessing

Numeric features:

- median imputation;
- min-max scaling.

Categorical features:

- most-frequent imputation;
- one-hot encoding;
- unknown values ignored at inference.

The preprocessing pipeline is fitted on training data only because it is
contained inside each scikit-learn model pipeline.

## Evaluation discipline

The data is split into:

- 70% train;
- 15% validation;
- 15% test.

Model selection uses validation metrics. Final reporting also includes a
separate test set. This prevents the test set from becoming part of model
selection.

## Local workflow

Inspect:

```powershell
python scripts/inspect_awid3.py "C:\path\to\AWID3.csv"
```

Train:

```powershell
python scripts/train_awid3.py "C:\path\to\AWID3.csv"
```

If your label field is named differently:

```powershell
python scripts/train_awid3.py "C:\path\to\AWID3.csv" --label-column Label
```
