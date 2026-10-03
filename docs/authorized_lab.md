# Authorized Security Lab

## Purpose

The lab layer binds telemetry and analysis to equipment that the operator owns
or is explicitly authorized to test.

## Target registration

A target records:

- target ID;
- friendly name;
- SSID;
- BSSID;
- authorization flag;
- owner/authorization confirmation;
- notes;
- creation time.

The registry rejects targets without explicit authorization.

## Session lifecycle

A lab session records:

- target;
- mode;
- sensor source;
- created/start/end timestamps;
- before/after feature snapshots;
- sensor-session evidence path;
- failure information.

## Evidence

Evidence bundles hash attached files with SHA-256 so the report can show that a
specific artifact was not silently replaced after the experiment.

## Before/after analysis

VantaWave compares numeric feature windows and records:

- before;
- after;
- absolute change;
- percentage change.

## Incidents

A lab session may create an incident using measured anomaly/classifier evidence
and the transparent Risk Engine.

The incident system does not invent attack evidence.
