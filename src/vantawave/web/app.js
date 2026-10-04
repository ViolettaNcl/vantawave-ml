const $ = (id) => document.getElementById(id);

const state = {
  cache: new Map(),
  captureAuditId: null,
  captureSecretToken: null,
  title: {
    overview: "Overview",
    live: "Live Monitor",
    recovery: "Wi-Fi Recovery",
    capture: "Capture Audit",
    incidents: "Incidents",
    models: "Models",
    experiments: "Experiments",
    lab: "Authorized Lab",
    monitoring: "Monitoring",
    analyst: "AI Analyst",
  },
};

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body);
    } catch {}
    throw new Error(detail);
  }
  return response.json();
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function badge(value, cls = "neutral") {
  return `<span class="badge ${cls}">${esc(value)}</span>`;
}

function yesNo(value) {
  return value ? badge("available", "good") : badge("not available", "neutral");
}

function renderList(container, items, emptyText = "No data yet.") {
  container.innerHTML = items.length ? items.join("") : `<div class="empty">${esc(emptyText)}</div>`;
}

function severityClass(value) {
  const v = String(value || "").toUpperCase();
  if (["HIGH", "CRITICAL"].includes(v)) return "bad";
  if (v === "MEDIUM") return "warn";
  return "good";
}

async function loadOverview() {
  const [health, ready, ml, sensor, registry, labTargets] = await Promise.all([
    api("/health"),
    api("/ready"),
    api("/mlops/capabilities"),
    api("/sensors/capabilities"),
    api("/registry/models"),
    api("/lab/targets"),
  ]);

  $("metric-system").textContent = health.version || "online";
  $("metric-system-sub").textContent = ready.ready ? "Ready" : "Degraded";
  $("metric-sensor").textContent = sensor.host?.operating_system || "—";
  $("metric-sensor-sub").textContent = sensor.host?.passive_windows_scan ? "Windows scan available" : "Replay / limited live mode";
  $("metric-models").textContent = registry.models?.length ?? 0;
  $("metric-models-sub").textContent = "Registered versions";
  $("sidebar-health").textContent = ready.ready ? "Ready" : "Needs attention";
  document.querySelector(".status-dot").style.background = ready.ready ? "var(--good)" : "var(--warn)";

  $("readiness-badge").textContent = ready.ready ? "Ready" : "Degraded";
  $("readiness-badge").className = `badge ${ready.ready ? "good" : "warn"}`;
  renderList($("readiness-list"), (ready.checks || []).map(c => `
    <div class="list-item">
      <div><div class="list-title">${esc(c.name)}</div><div class="list-sub">${esc(c.detail)}</div></div>
      ${c.ok ? badge("OK","good") : badge("FAIL","bad")}
    </div>
  `));

  $("ml-capabilities").innerHTML = Object.entries(ml).map(([key, value]) => `
    <div class="cap"><span>${esc(key.replaceAll("_"," "))}</span><span>${value ? "✓" : "—"}</span></div>
  `).join("");

  renderList($("overview-targets"), (labTargets.targets || []).slice(0,5).map(t => `
    <div class="list-item">
      <div><div class="list-title">${esc(t.name)}</div><div class="list-sub">${esc(t.ssid)} • ${esc(t.bssid)}</div></div>
      ${badge(t.authorized ? "authorized" : "blocked", t.authorized ? "good" : "bad")}
    </div>
  `), "No authorized targets registered.");

  try {
    const monitoring = await api("/monitoring/recent");
    renderList($("overview-drift"), (monitoring.drift_events || []).slice(0,5).map(d => `
      <div class="list-item">
        <div><div class="list-title">${esc(d.feature)}</div><div class="list-sub">${esc(d.kind)} • score ${Number(d.score || 0).toFixed(3)}</div></div>
        ${badge(d.severity, severityClass(d.severity))}
      </div>
    `), "No drift records yet.");
  } catch (error) {
    $("overview-drift").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }

  try {
    const incidents = await api("/incidents");
    $("metric-incidents").textContent = incidents.incidents?.length ?? 0;
    $("metric-incidents-sub").textContent = "Persisted incidents";
  } catch {
    $("metric-incidents").textContent = "—";
  }
}

async function loadLive() {
  const caps = await api("/sensors/capabilities");
  $("sensor-capabilities").textContent = JSON.stringify(caps, null, 2);
}

async function scanWifi() {
  $("wifi-results").innerHTML = `<div class="empty">Scanning…</div>`;
  try {
    const result = await api("/sensors/windows/scan");
    renderList($("wifi-results"), (result.events || []).map(e => `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(e.ssid || "Hidden SSID")}</div>
          <div class="list-sub">${esc(e.bssid)} • channel ${esc(e.channel)} • ${esc(e.security || "unknown security")}</div>
        </div>
        ${badge(e.signal_percent != null ? `${e.signal_percent}%` : "—", "neutral")}
      </div>
    `), "No networks returned by Windows.");
  } catch (error) {
    $("wifi-results").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}


async function loadRecovery() {
  const capabilities = await api("/wifi-recovery/capabilities");
  const profiles = await api("/wifi-recovery/profiles");

  renderList($("recovery-profiles"), (profiles.profiles || []).map(profile => `
    <div class="list-item network-select" data-profile="${esc(profile.name)}">
      <div>
        <div class="list-title">${esc(profile.name)}</div>
        <div class="list-sub">Windows saved profile</div>
      </div>
      ${badge("saved", "good")}
    </div>
  `), "No saved Windows Wi-Fi profiles.");

  document.querySelectorAll("[data-profile]").forEach(item => {
    item.addEventListener("click", () => {
      $("recovery-ssid").value = item.dataset.profile;
      checkRecoveryStatus();
    });
  });

  if (!capabilities.saved_key_view_enabled) {
    $("recovery-show-key").disabled = true;
    $("recovery-show-key").title =
      "Set VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW=true before starting VantaWave to enable local saved-key viewing.";
  }

  try {
    const gateways = await api("/wifi-recovery/gateways");
    renderList($("recovery-gateways"), (gateways.gateways || []).map(g => `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(g.gateway || "Unknown gateway")}</div>
          <div class="list-sub">${esc(g.interface_alias || "Unknown interface")} • index ${esc(g.interface_index ?? "—")}</div>
        </div>
        ${g.gateway ? `<a class="ghost" href="http://${esc(g.gateway)}" target="_blank" rel="noreferrer">Open</a>` : ""}
      </div>
    `), "No default gateway is currently visible.");
  } catch (error) {
    $("recovery-gateways").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function scanRecoveryNetworks() {
  $("recovery-networks").innerHTML = `<div class="empty">Scanning…</div>`;
  try {
    const result = await api("/wifi-recovery/nearby");
    const bySsid = new Map();
    for (const network of (result.networks || [])) {
      const key = network.ssid || `(hidden:${network.bssid || "unknown"})`;
      const previous = bySsid.get(key);
      if (!previous || (network.signal_percent ?? -1) > (previous.signal_percent ?? -1)) {
        bySsid.set(key, network);
      }
    }

    renderList($("recovery-networks"), [...bySsid.values()].map(n => `
      <div class="list-item network-select recovery-network"
           data-ssid="${esc(n.ssid || "")}"
           data-security="${esc(n.security || "")}">
        <div>
          <div class="list-title">${esc(n.ssid || "Hidden SSID")}</div>
          <div class="list-sub">
            ${esc(n.bssid || "—")} • channel ${esc(n.channel ?? "—")} • ${esc(n.security || "unknown security")}
          </div>
        </div>
        ${badge(n.signal_percent != null ? `${n.signal_percent}%` : "—", "neutral")}
      </div>
    `), "No OS-visible Wi-Fi networks returned.");

    document.querySelectorAll(".recovery-network").forEach(item => {
      item.addEventListener("click", () => {
        $("recovery-ssid").value = item.dataset.ssid || "";
        const security = (item.dataset.security || "").toUpperCase();
        $("recovery-security").value =
          security.includes("WPA3") ? "WPA3-Personal" : "WPA2-Personal";
        checkRecoveryStatus();
      });
    });
  } catch (error) {
    $("recovery-networks").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function checkRecoveryStatus() {
  const ssid = $("recovery-ssid").value.trim();
  if (!ssid) {
    $("recovery-status").innerHTML = `<div class="empty">SSID is required.</div>`;
    return;
  }

  $("recovery-status").innerHTML = `<div class="empty">Checking local Windows/router recovery state…</div>`;

  try {
    const status = await api(`/wifi-recovery/status?ssid=${encodeURIComponent(ssid)}`);
    renderList($("recovery-status"), (status.recovery_options || []).map(option => `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(option.title)}</div>
          <div class="list-sub">${esc(option.description)}</div>
        </div>
        ${badge(option.available ? "available" : "not available", option.available ? "good" : "neutral")}
      </div>
    `));

    if (!status.saved_profile) {
      $("recovery-key").textContent =
        "No saved Windows key exists for this SSID on this laptop.";
    } else {
      $("recovery-key").textContent =
        "Saved profile detected. Use Show saved key if local secret viewing is enabled.";
    }
  } catch (error) {
    $("recovery-status").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function showRecoverySavedKey() {
  const ssid = $("recovery-ssid").value.trim();
  if (!ssid) {
    $("recovery-key").textContent = "SSID is required.";
    return;
  }

  $("recovery-key").textContent = "Reading local Windows profile…";

  try {
    const result = await api("/wifi-recovery/saved-key", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        ssid,
        explicit_confirmation: true,
      }),
    });

    $("recovery-key").textContent = result.saved
      ? result.password
      : result.message;
  } catch (error) {
    $("recovery-key").textContent = error.message;
  }
}

async function auditRecoveryPassword() {
  const password = $("recovery-password").value;
  if (!password) {
    $("recovery-password-audit").innerHTML =
      `<div class="empty">Enter a password to audit locally.</div>`;
    return;
  }

  try {
    const result = await api("/wifi-recovery/password-strength", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({password}),
    });

    renderList($("recovery-password-audit"), [
      `<div class="list-item">
        <div>
          <div class="list-title">Local strength: ${esc(result.rating)}</div>
          <div class="list-sub">Score ${esc(result.score)}/100 • estimated entropy ${Number(result.estimated_entropy_bits || 0).toFixed(1)} bits</div>
        </div>
        ${badge(`${result.score}/100`, result.score >= 60 ? "good" : result.score >= 40 ? "warn" : "bad")}
      </div>`,
      ...(result.findings || []).map(f => `
        <div class="list-item">
          <div><div class="list-title">Finding</div><div class="list-sub">${esc(f)}</div></div>
        </div>
      `),
    ]);
  } catch (error) {
    $("recovery-password-audit").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function connectRecoveryNetwork() {
  const ssid = $("recovery-ssid").value.trim();
  const password = $("recovery-password").value;
  const security = $("recovery-security").value;

  if (!ssid || !password) {
    $("recovery-password-audit").innerHTML =
      `<div class="empty">SSID and password are required to connect.</div>`;
    return;
  }

  $("recovery-password-audit").innerHTML =
    `<div class="empty">Sending a local Windows connection request…</div>`;

  try {
    const result = await api("/wifi-recovery/connect", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ssid, password, security}),
    });

    $("recovery-password-audit").innerHTML = `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(result.message)}</div>
          <div class="list-sub">
            SSID ${esc(result.ssid)} • ${esc(result.security)}.
            Windows now owns the resulting saved profile if the profile was accepted.
          </div>
        </div>
        ${badge(result.success ? "requested" : "failed", result.success ? "good" : "bad")}
      </div>`;
  } catch (error) {
    $("recovery-password-audit").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function deleteRecoveryProfile() {
  const ssid = $("recovery-ssid").value.trim();
  if (!ssid) return;

  if (!window.confirm(`Remove the saved Windows Wi-Fi profile "${ssid}" from this laptop?`)) {
    return;
  }

  try {
    const result = await api(`/wifi-recovery/profiles/${encodeURIComponent(ssid)}`, {
      method: "DELETE",
    });
    $("recovery-key").textContent = result.message;
    await loadRecovery();
    await checkRecoveryStatus();
  } catch (error) {
    $("recovery-key").textContent = error.message;
  }
}


async function loadCaptureAudit() {
  const [capabilities, targets] = await Promise.all([
    api("/capture-audit/capabilities"),
    api("/lab/targets"),
  ]);

  const targetSelect = $("capture-target");
  const authorizedTargets = (targets.targets || []).filter(t => t.authorized);

  targetSelect.innerHTML = authorizedTargets.length
    ? authorizedTargets.map(t =>
        `<option value="${esc(t.target_id)}">${esc(t.name)} — ${esc(t.ssid)} — ${esc(t.bssid)}</option>`
      ).join("")
    : `<option value="">No authorized targets registered</option>`;

  renderList($("capture-capabilities"), [
    `<div class="list-item">
      <div>
        <div class="list-title">Aircrack-ng</div>
        <div class="list-sub">${esc(capabilities.aircrack_ng?.reason || capabilities.aircrack_ng?.executable || "Available")}</div>
      </div>
      ${badge(capabilities.aircrack_ng?.available ? "available" : "not installed", capabilities.aircrack_ng?.available ? "good" : "warn")}
    </div>`,
    `<div class="list-item">
      <div>
        <div class="list-title">SSID-only recovery</div>
        <div class="list-sub">An unknown WPA2/WPA3 password cannot be derived from an SSID alone.</div>
      </div>
      ${badge("not supported", "neutral")}
    </div>`,
    `<div class="list-item">
      <div>
        <div class="list-title">Candidate verification</div>
        <div class="list-sub">Exactly one locally supplied WPA2 candidate per verification request.</div>
      </div>
      ${badge(capabilities.single_candidate_verification ? "ready" : "requires aircrack-ng", capabilities.single_candidate_verification ? "good" : "warn")}
    </div>`,
  ]);
}

async function uploadCaptureAudit() {
  const targetId = $("capture-target").value;
  const file = $("capture-file").files?.[0];

  if (!targetId) {
    $("capture-report").innerHTML =
      `<div class="empty">Register/select an Authorized Lab target first.</div>`;
    return;
  }
  if (!file) {
    $("capture-report").innerHTML =
      `<div class="empty">Select a .pcap, .pcapng or .cap file.</div>`;
    return;
  }

  $("capture-report").innerHTML =
    `<div class="empty">Uploading and analyzing capture…</div>`;
  state.captureAuditId = null;
  state.captureSecretToken = null;
  $("capture-masked-secret").textContent = "Not verified";
  $("capture-copy-secret").disabled = true;
  $("capture-connect").disabled = true;

  const form = new FormData();
  form.append("target_id", targetId);
  form.append("capture", file);

  try {
    const result = await api("/capture-audit/upload", {
      method: "POST",
      body: form,
    });

    state.captureAuditId = result.audit_id;
    const c = result.capture || {};

    renderList($("capture-report"), [
      `<div class="list-item">
        <div>
          <div class="list-title">${esc(result.target?.ssid || "Target")}</div>
          <div class="list-sub">${esc(result.target?.bssid || "—")} • audit ${esc(result.audit_id)}</div>
        </div>
        ${badge(c.target_seen ? "target seen" : "not seen", c.target_seen ? "good" : "bad")}
      </div>`,
      `<div class="list-item">
        <div>
          <div class="list-title">802.11 packets</div>
          <div class="list-sub">${esc(c.dot11_packets ?? 0)} of ${esc(c.total_packets ?? 0)} total packets</div>
        </div>
        ${badge(String(c.target_packets ?? 0), "neutral")}
      </div>`,
      `<div class="list-item">
        <div>
          <div class="list-title">Target EAPOL evidence</div>
          <div class="list-sub">${esc(c.target_eapol_packets ?? 0)} matching EAPOL frame(s)</div>
        </div>
        ${badge(c.likely_handshake_evidence ? "multiple frames" : "insufficient/none", c.likely_handshake_evidence ? "good" : "warn")}
      </div>`,
      `<div class="list-item">
        <div>
          <div class="list-title">Candidate verification</div>
          <div class="list-sub">${(c.notes || []).map(esc).join(" ")}</div>
        </div>
        ${badge(c.candidate_verification_ready ? "eligible" : "not ready", c.candidate_verification_ready ? "good" : "warn")}
      </div>`,
    ]);
  } catch (error) {
    $("capture-report").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function verifyCaptureCandidate() {
  const candidate = $("capture-candidate").value;
  const security = $("capture-security").value;

  if (!state.captureAuditId) {
    $("capture-verification").innerHTML =
      `<div class="empty">Analyze an authorized capture first.</div>`;
    return;
  }
  if (!candidate) {
    $("capture-verification").innerHTML =
      `<div class="empty">Enter one WPA2 password candidate.</div>`;
    return;
  }

  $("capture-verification").innerHTML =
    `<div class="empty">Asking Aircrack-ng to verify this single candidate…</div>`;

  try {
    const result = await api("/capture-audit/verify-candidate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        audit_id: state.captureAuditId,
        candidate,
        security,
      }),
    });

    state.captureSecretToken = result.secret_token || null;

    $("capture-verification").innerHTML = `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(result.message)}</div>
          <div class="list-sub">The candidate itself is not written into the capture report or VantaWave logs.</div>
        </div>
        ${badge(result.verified ? "verified" : "not verified", result.verified ? "good" : "bad")}
      </div>`;

    if (result.verified && result.secret_token) {
      $("capture-masked-secret").textContent = result.masked_secret || "••••••••";
      $("capture-connect").disabled = false;
      $("capture-copy-secret").disabled = false;
      $("capture-candidate").value = "";
    } else {
      $("capture-masked-secret").textContent = "Not verified";
      $("capture-connect").disabled = true;
      $("capture-copy-secret").disabled = true;
    }
  } catch (error) {
    state.captureSecretToken = null;
    $("capture-masked-secret").textContent = "Not verified";
    $("capture-connect").disabled = true;
    $("capture-copy-secret").disabled = true;
    $("capture-verification").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function connectVerifiedCaptureSecret() {
  if (!state.captureSecretToken) return;

  $("capture-connect-result").innerHTML =
    `<div class="empty">Requesting Windows connection with the verified in-memory secret…</div>`;

  try {
    const result = await api("/capture-audit/connect-verified", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({token: state.captureSecretToken}),
    });

    $("capture-connect-result").innerHTML = `
      <div class="list-item">
        <div>
          <div class="list-title">${esc(result.message)}</div>
          <div class="list-sub">${esc(result.ssid || "SSID")} • ${esc(result.security || "")}</div>
        </div>
        ${badge(result.success ? "connected" : (result.request_accepted ? "requested" : "failed"), result.success ? "good" : "warn")}
      </div>`;
  } catch (error) {
    $("capture-connect-result").innerHTML =
      `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function copyVerifiedCaptureSecret() {
  if (!state.captureSecretToken) return;

  try {
    const result = await api(`/capture-audit/secret/${encodeURIComponent(state.captureSecretToken)}`);
    await navigator.clipboard.writeText(result.password);
    $("capture-connect-result").innerHTML = `
      <div class="list-item">
        <div>
          <div class="list-title">Verified secret copied locally</div>
          <div class="list-sub">The visible mask is not the password; the clipboard received the actual verified in-memory candidate.</div>
        </div>
        ${badge("copied", "good")}
      </div>`;
  } catch (error) {
    $("capture-connect-result").innerHTML =
      `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function loadIncidents() {
  try {
    const result = await api("/incidents");
    const incidents = result.incidents || [];
    $("incidents-list").innerHTML = incidents.length ? `
      <table><thead><tr><th>ID</th><th>Title</th><th>Severity</th><th>Risk</th><th>Prediction</th><th>Created</th></tr></thead>
      <tbody>${incidents.map(e => `
        <tr>
          <td><button class="ghost incident-pick" data-id="${esc(e.incident_id)}">${esc(e.incident_id)}</button></td>
          <td>${esc(e.title)}</td>
          <td>${badge(e.severity || "INFO", severityClass(e.severity))}</td>
          <td>${esc(e.risk_score ?? "—")}</td>
          <td>${esc(e.predicted_class || "—")}</td>
          <td>${esc(e.created_at || "—")}</td>
        </tr>`).join("")}</tbody></table>` : `<div class="empty">No persisted incidents yet.</div>`;

    document.querySelectorAll(".incident-pick").forEach(button => {
      button.addEventListener("click", () => {
        $("analyst-incident-id").value = button.dataset.id;
        activateView("analyst");
      });
    });
  } catch (error) {
    $("incidents-list").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function loadModels() {
  const [registry, policy] = await Promise.all([api("/registry/models"), api("/promotion/policy")]);
  renderList($("models-list"), (registry.models || []).map(m => `
    <div class="list-item">
      <div><div class="list-title">${esc(m.model_name)} v${esc(m.version)}</div><div class="list-sub">${esc(m.status)} • threshold ${esc(m.threshold)}</div></div>
      ${badge((m.aliases || []).join(", ") || "candidate", m.status === "champion" ? "good" : "neutral")}
    </div>
  `), "No registered models yet.");
  $("promotion-policy").textContent = JSON.stringify(policy, null, 2);
}

async function loadExperiments() {
  const result = await api("/experiments");
  renderList($("experiments-list"), (result.runs || []).map(r => `
    <div class="list-item">
      <div><div class="list-title">${esc(r.name)} • ${esc(r.run_id)}</div><div class="list-sub">${esc(r.version)} • ${esc(r.created_at)}</div></div>
      ${badge(r.status || "completed", "good")}
    </div>
  `), "No experiment runs yet.");
}

async function loadLab() {
  const [targets, sessions] = await Promise.all([api("/lab/targets"), api("/lab/sessions")]);
  renderList($("lab-targets"), (targets.targets || []).map(t => `
    <div class="list-item">
      <div><div class="list-title">${esc(t.name)}</div><div class="list-sub">${esc(t.ssid)} • ${esc(t.bssid)}</div></div>
      ${badge(t.authorized ? "authorized" : "blocked", t.authorized ? "good" : "bad")}
    </div>
  `), "No targets registered.");
  renderList($("lab-sessions"), (sessions.sessions || []).map(s => `
    <div class="list-item">
      <div><div class="list-title">${esc(s.session_id)}</div><div class="list-sub">${esc(s.mode)} • ${esc(s.sensor_source)}</div></div>
      ${badge(s.status, s.status === "completed" ? "good" : "neutral")}
    </div>
  `), "No lab sessions yet.");
}

async function loadMonitoring() {
  const policy = await api("/monitoring/policy");
  $("monitoring-policy").textContent = JSON.stringify(policy, null, 2);
  try {
    const recent = await api("/monitoring/recent");
    renderList($("monitoring-evaluations"), (recent.evaluations || []).map(e => `
      <div class="list-item">
        <div><div class="list-title">${esc(e.model_name)}</div><div class="list-sub">${esc(e.dataset_name)} • ${esc(e.recommendation)}</div></div>
        ${badge(e.status || "completed","good")}
      </div>
    `), "No evaluations persisted.");

    const drift = recent.drift_events || [];
    $("monitoring-drift").innerHTML = drift.length ? `
      <table><thead><tr><th>Feature</th><th>Kind</th><th>Score</th><th>Severity</th><th>Created</th></tr></thead>
      <tbody>${drift.map(d => `
        <tr><td>${esc(d.feature)}</td><td>${esc(d.kind)}</td><td>${Number(d.score || 0).toFixed(4)}</td>
        <td>${badge(d.severity, severityClass(d.severity))}</td><td>${esc(d.created_at || "—")}</td></tr>`).join("")}</tbody></table>` :
      `<div class="empty">No drift events persisted.</div>`;
  } catch (error) {
    $("monitoring-evaluations").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
    $("monitoring-drift").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

function renderAnalyst(report) {
  const findings = report.findings || [];
  const evidence = report.evidence || [];
  const contexts = report.retrieved_context || [];
  return `
    <p>${esc(report.summary)}</p>
    <h3>Findings</h3>
    ${findings.length ? `<ul>${findings.map(f => `
      <li><strong class="sev-${esc(f.severity)}">${esc(f.title)}</strong>: ${esc(f.statement)}
      ${(f.citations || []).map(c => `<span class="citation">${esc(c)}</span>`).join(" ")}</li>
    `).join("")}</ul>` : `<div class="empty">No concrete findings.</div>`}
    <h3>Defensive actions</h3>
    <ul>${(report.defensive_actions || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
    <h3>Evidence</h3>
    <ul>${evidence.map(e => `<li><span class="citation">${esc(e.citation)}</span> ${esc(e.label)}</li>`).join("")}</ul>
    <h3>Retrieved context</h3>
    <ul>${contexts.map(c => `<li><span class="citation">${esc(c.citation)}</span> ${esc(c.chunk?.title || "Knowledge")} • score ${Number(c.score || 0).toFixed(3)}</li>`).join("")}</ul>
    <h3>Limitations</h3>
    <ul>${(report.limitations || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
  `;
}

async function analyzeIncident() {
  const incidentId = $("analyst-incident-id").value.trim();
  const query = $("analyst-query").value.trim();
  if (!incidentId) {
    $("analyst-result").innerHTML = `<div class="empty">Incident ID is required.</div>`;
    return;
  }
  $("analyst-result").innerHTML = `<div class="empty">Analyzing persisted evidence…</div>`;
  try {
    const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
    const report = await api(`/ai/analyze/${encodeURIComponent(incidentId)}${suffix}`);
    $("analyst-result").innerHTML = renderAnalyst(report);
  } catch (error) {
    $("analyst-result").innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  }
}

async function loadView(view) {
  try {
    if (view === "overview") await loadOverview();
    if (view === "live") await loadLive();
    if (view === "recovery") await loadRecovery();
    if (view === "capture") await loadCaptureAudit();
    if (view === "incidents") await loadIncidents();
    if (view === "models") await loadModels();
    if (view === "experiments") await loadExperiments();
    if (view === "lab") await loadLab();
    if (view === "monitoring") await loadMonitoring();
  } catch (error) {
    console.error(error);
  }
}

function activateView(view) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(v => v.classList.remove("active"));
  $(`view-${view}`).classList.add("active");
  document.querySelector(`[data-view="${view}"]`).classList.add("active");
  $("view-title").textContent = state.title[view] || view;
  loadView(view);
}

document.querySelectorAll(".nav-item").forEach(button => {
  button.addEventListener("click", () => activateView(button.dataset.view));
});
$("refresh").addEventListener("click", () => {
  const active = document.querySelector(".nav-item.active")?.dataset.view || "overview";
  loadView(active);
});
$("scan-wifi").addEventListener("click", scanWifi);
$("analyze-incident").addEventListener("click", analyzeIncident);

$("recovery-scan").addEventListener("click", scanRecoveryNetworks);
$("recovery-refresh-profiles").addEventListener("click", loadRecovery);
$("recovery-check-status").addEventListener("click", checkRecoveryStatus);
$("recovery-show-key").addEventListener("click", showRecoverySavedKey);
$("recovery-audit-password").addEventListener("click", auditRecoveryPassword);
$("recovery-connect").addEventListener("click", connectRecoveryNetwork);
$("recovery-delete-profile").addEventListener("click", deleteRecoveryProfile);

$("capture-upload").addEventListener("click", uploadCaptureAudit);
$("capture-verify").addEventListener("click", verifyCaptureCandidate);
$("capture-connect").addEventListener("click", connectVerifiedCaptureSecret);
$("capture-copy-secret").addEventListener("click", copyVerifiedCaptureSecret);

loadOverview();
