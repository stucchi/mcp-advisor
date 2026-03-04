"""Embedded MCP App HTML views for Claude Desktop UI."""

# ---------------------------------------------------------------------------
# Search / Trending view — used by search_servers and get_trending_servers
# ---------------------------------------------------------------------------

SEARCH_VIEW_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root { color-scheme: light dark; }
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
    color: light-dark(#1a1a2e, #e4e4e7);
    background: transparent;
    padding: 12px;
  }

  .card {
    border: 1px solid light-dark(#e4e4e7, #3f3f46);
    border-radius: 12px;
    overflow: hidden;
    max-width: 600px;
  }

  /* Summary bar */
  .summary {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid light-dark(#e4e4e7, #3f3f46);
    font-size: 13px;
    color: light-dark(#71717a, #a1a1aa);
  }

  .summary-count {
    font-weight: 700;
    color: light-dark(#1a1a2e, #e4e4e7);
  }

  .summary-query {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 12px;
    background: light-dark(#f4f4f5, #27272a);
    padding: 2px 8px;
    border-radius: 4px;
  }

  /* Server list */
  .servers {
    max-height: 500px;
    overflow-y: auto;
  }

  .server {
    display: flex;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid light-dark(#f4f4f5, #27272a);
  }

  .server:last-child { border-bottom: none; }

  .server-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    flex-shrink: 0;
    background: light-dark(#f4f4f5, #27272a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    overflow: hidden;
  }

  .server-icon img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .server-body { flex: 1; min-width: 0; }

  .server-title {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .server-name {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 11px;
    color: light-dark(#71717a, #a1a1aa);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .server-desc {
    font-size: 12px;
    color: light-dark(#52525b, #a1a1aa);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 6px;
  }

  .server-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .stat {
    display: flex;
    align-items: center;
    gap: 3px;
    font-size: 11px;
    color: light-dark(#71717a, #a1a1aa);
    font-weight: 500;
  }

  .stat-icon { font-size: 12px; }

  .badge {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 1px 6px;
    border-radius: 4px;
    background: light-dark(#ede9fe, #2e1065);
    color: light-dark(#7c3aed, #c4b5fd);
  }

  .badge.npm { background: light-dark(#fef3c7, #451a03); color: light-dark(#b45309, #fbbf24); }
  .badge.pypi { background: light-dark(#dbeafe, #172554); color: light-dark(#2563eb, #93c5fd); }
  .badge.oci { background: light-dark(#dcfce7, #052e16); color: light-dark(#16a34a, #86efac); }

  .badge.sec-none { background: light-dark(#dcfce7, #052e16); color: light-dark(#16a34a, #86efac); }
  .badge.sec-low { background: light-dark(#fefce8, #422006); color: light-dark(#a16207, #facc15); }
  .badge.sec-medium { background: light-dark(#fff7ed, #431407); color: light-dark(#c2410c, #fb923c); }
  .badge.sec-high { background: light-dark(#fef2f2, #450a0a); color: light-dark(#dc2626, #fca5a5); }
  .badge.sec-critical { background: light-dark(#fef2f2, #450a0a); color: light-dark(#dc2626, #fca5a5); font-weight: 700; }

  .tags {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin-top: 4px;
  }

  .tag {
    font-size: 10px;
    padding: 1px 5px;
    border-radius: 3px;
    background: light-dark(#f4f4f5, #27272a);
    color: light-dark(#71717a, #a1a1aa);
  }

  /* Loading */
  .loading {
    padding: 32px;
    text-align: center;
    color: light-dark(#71717a, #a1a1aa);
    font-size: 14px;
  }

  .spinner {
    display: inline-block;
    width: 22px;
    height: 22px;
    border: 2.5px solid light-dark(#e4e4e7, #3f3f46);
    border-top-color: light-dark(#2563eb, #60a5fa);
    border-radius: 50%;
    animation: spin .7s linear infinite;
    margin-bottom: 10px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .empty {
    padding: 32px;
    text-align: center;
    color: light-dark(#71717a, #a1a1aa);
    font-size: 13px;
  }
</style>
</head>
<body>
<div class="card">
  <div id="content">
    <div class="loading">
      <div class="spinner"></div>
      <div>Searching servers&#8230;</div>
    </div>
  </div>
</div>

<script type="module">
import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@1.1.2/dist/src/app-with-deps.js";

var app = new App(
  { name: "MCP Advisor Search", version: "1.0.0" },
  {},
  { autoResize: true }
);

function esc(s) {
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function renderServer(s) {
  var iconHtml;
  if (s.icon_url) {
    iconHtml = '<img src="' + esc(s.icon_url) + '" alt="">';
  } else {
    iconHtml = '&#9881;';
  }

  var badges = '';
  var pkgs = s.packages || [];
  for (var i = 0; i < pkgs.length; i++) {
    var p = pkgs[i];
    if (p.transport) badges += '<span class="badge">' + esc(p.transport) + '</span>';
    if (p.registry_type) badges += '<span class="badge ' + esc(p.registry_type) + '">' + esc(p.registry_type) + '</span>';
  }

  var tags = '';
  if (s.tags && s.tags.length > 0) {
    tags = '<div class="tags">';
    var maxTags = Math.min(s.tags.length, 4);
    for (var t = 0; t < maxTags; t++) {
      tags += '<span class="tag">' + esc(s.tags[t]) + '</span>';
    }
    if (s.tags.length > maxTags) tags += '<span class="tag">+' + (s.tags.length - maxTags) + '</span>';
    tags += '</div>';
  }

  var secBadge = '';
  if (s.security) {
    var sl = s.security.risk_level;
    if (sl === 'none') secBadge = '<span class="badge sec-none">&#10003; Scanned</span>';
    else if (sl === 'low') secBadge = '<span class="badge sec-low">Low risk</span>';
    else if (sl === 'medium') secBadge = '<span class="badge sec-medium">Medium risk</span>';
    else if (sl === 'high') secBadge = '<span class="badge sec-high">High risk</span>';
    else if (sl === 'critical') secBadge = '<span class="badge sec-critical">Critical risk</span>';
  }

  var stars = s.star_count != null ? s.star_count : (s.stars != null ? s.stars : 0);
  var installs = s.install_count != null ? s.install_count : (s.total_installs != null ? s.total_installs : 0);

  return '<div class="server">' +
    '<div class="server-icon">' + iconHtml + '</div>' +
    '<div class="server-body">' +
      '<div class="server-title">' + esc(s.title || s.display_name || s.name || '') + '</div>' +
      '<div class="server-name">' + esc(s.name || '') + '</div>' +
      (s.description ? '<div class="server-desc">' + esc(s.description) + '</div>' : '') +
      '<div class="server-meta">' +
        '<span class="stat"><span class="stat-icon">&#9733;</span> ' + stars + '</span>' +
        '<span class="stat"><span class="stat-icon">&#8615;</span> ' + installs + '</span>' +
        secBadge +
        badges +
      '</div>' +
      tags +
    '</div>' +
  '</div>';
}

function render(data) {
  var el = document.getElementById("content");
  var servers = data.servers || data.results || [];
  if (servers.length === 0) {
    el.innerHTML = '<div class="empty">No servers found.</div>';
    return;
  }

  var summaryHtml = '<div class="summary"><span class="summary-count">' + servers.length + ' server' + (servers.length !== 1 ? 's' : '') + '</span>';
  if (data.query) {
    summaryHtml += '<span class="summary-query">' + esc(data.query) + '</span>';
  }
  summaryHtml += '</div>';

  var listHtml = '<div class="servers">';
  for (var i = 0; i < servers.length; i++) {
    listHtml += renderServer(servers[i]);
  }
  listHtml += '</div>';

  el.innerHTML = summaryHtml + listHtml;
}

function showLoading() {
  document.getElementById("content").innerHTML =
    '<div class="loading"><div class="spinner"></div><div>Searching servers&#8230;</div></div>';
}

app.ontoolinput = function() { showLoading(); };

app.ontoolresult = function(result) {
  var data = result.structuredContent;
  if (!data && result.content && result.content[0]) {
    try { data = JSON.parse(result.content[0].text); } catch(e) { data = {}; }
  }
  render(data || {});
};

app.onhostcontextchanged = function(ctx) {
  if (ctx.theme) document.documentElement.style.colorScheme = ctx.theme;
};

await app.connect();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Detail view — used by get_server_details
# ---------------------------------------------------------------------------

DETAIL_VIEW_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root { color-scheme: light dark; }
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
    color: light-dark(#1a1a2e, #e4e4e7);
    background: transparent;
    padding: 12px;
  }

  .card {
    border: 1px solid light-dark(#e4e4e7, #3f3f46);
    border-radius: 12px;
    overflow: hidden;
    max-width: 560px;
  }

  /* Header */
  .header {
    display: flex;
    gap: 14px;
    padding: 20px 16px 16px;
    align-items: flex-start;
  }

  .header-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    flex-shrink: 0;
    background: light-dark(#f4f4f5, #27272a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    overflow: hidden;
  }

  .header-icon img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .header-text { flex: 1; min-width: 0; }

  .header-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 2px;
  }

  .header-name {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 12px;
    color: light-dark(#71717a, #a1a1aa);
  }

  /* Description */
  .desc {
    padding: 0 16px 14px;
    font-size: 13px;
    line-height: 1.5;
    color: light-dark(#52525b, #a1a1aa);
  }

  /* Stats row */
  .stats {
    display: flex;
    border-top: 1px solid light-dark(#e4e4e7, #3f3f46);
    border-bottom: 1px solid light-dark(#e4e4e7, #3f3f46);
  }

  .stat-item {
    flex: 1;
    text-align: center;
    padding: 12px 8px;
    border-right: 1px solid light-dark(#e4e4e7, #3f3f46);
  }

  .stat-item:last-child { border-right: none; }

  .stat-num {
    font-size: 20px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 2px;
  }

  .stat-label {
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: light-dark(#71717a, #a1a1aa);
  }

  /* Meta section */
  .meta {
    padding: 12px 16px;
  }

  .meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    padding: 4px 0;
    color: light-dark(#52525b, #a1a1aa);
  }

  .meta-label {
    font-weight: 600;
    color: light-dark(#71717a, #a1a1aa);
    min-width: 70px;
  }

  .meta-value {
    word-break: break-all;
  }

  .meta-link {
    color: light-dark(#2563eb, #60a5fa);
    text-decoration: none;
  }

  /* Packages */
  .packages {
    padding: 0 16px 12px;
  }

  .packages-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: light-dark(#71717a, #a1a1aa);
    margin-bottom: 6px;
  }

  .pkg {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 0;
    font-size: 12px;
  }

  .pkg-name {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 12px;
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 1px 6px;
    border-radius: 4px;
    background: light-dark(#ede9fe, #2e1065);
    color: light-dark(#7c3aed, #c4b5fd);
    flex-shrink: 0;
  }

  .badge.npm { background: light-dark(#fef3c7, #451a03); color: light-dark(#b45309, #fbbf24); }
  .badge.pypi { background: light-dark(#dbeafe, #172554); color: light-dark(#2563eb, #93c5fd); }
  .badge.oci { background: light-dark(#dcfce7, #052e16); color: light-dark(#16a34a, #86efac); }

  .badge.sec-none { background: light-dark(#dcfce7, #052e16); color: light-dark(#16a34a, #86efac); }
  .badge.sec-low { background: light-dark(#fefce8, #422006); color: light-dark(#a16207, #facc15); }
  .badge.sec-medium { background: light-dark(#fff7ed, #431407); color: light-dark(#c2410c, #fb923c); }
  .badge.sec-high { background: light-dark(#fef2f2, #450a0a); color: light-dark(#dc2626, #fca5a5); }
  .badge.sec-critical { background: light-dark(#fef2f2, #450a0a); color: light-dark(#dc2626, #fca5a5); font-weight: 700; }

  /* Security section */
  .security {
    padding: 12px 16px;
    border-top: 1px solid light-dark(#e4e4e7, #3f3f46);
  }

  .security-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: light-dark(#71717a, #a1a1aa);
    margin-bottom: 8px;
  }

  .security-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: light-dark(#52525b, #a1a1aa);
    margin-bottom: 4px;
  }

  .findings {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .finding {
    display: flex;
    gap: 8px;
    align-items: flex-start;
    padding: 8px 10px;
    border-radius: 6px;
    background: light-dark(#fafafa, #1c1c1e);
    border: 1px solid light-dark(#e4e4e7, #3f3f46);
    font-size: 12px;
  }

  .finding-icon {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    margin-top: 1px;
  }

  .finding-icon.critical, .finding-icon.high {
    background: light-dark(#fef2f2, #450a0a);
    color: light-dark(#dc2626, #fca5a5);
  }

  .finding-icon.medium {
    background: light-dark(#fff7ed, #431407);
    color: light-dark(#c2410c, #fb923c);
  }

  .finding-icon.low {
    background: light-dark(#fefce8, #422006);
    color: light-dark(#a16207, #facc15);
  }

  .finding-body { flex: 1; min-width: 0; }

  .finding-type {
    font-weight: 600;
    color: light-dark(#1a1a2e, #e4e4e7);
    margin-bottom: 2px;
  }

  .finding-desc {
    color: light-dark(#52525b, #a1a1aa);
    line-height: 1.4;
  }

  .finding-tool {
    font-family: var(--font-mono, ui-monospace, monospace);
    font-size: 11px;
    color: light-dark(#71717a, #a1a1aa);
    margin-top: 3px;
  }

  /* Tags */
  .tags-section {
    padding: 0 16px 14px;
  }

  .tags {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .tag {
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 4px;
    background: light-dark(#f4f4f5, #27272a);
    color: light-dark(#71717a, #a1a1aa);
  }

  /* Loading */
  .loading {
    padding: 32px;
    text-align: center;
    color: light-dark(#71717a, #a1a1aa);
    font-size: 14px;
  }

  .spinner {
    display: inline-block;
    width: 22px;
    height: 22px;
    border: 2.5px solid light-dark(#e4e4e7, #3f3f46);
    border-top-color: light-dark(#2563eb, #60a5fa);
    border-radius: 50%;
    animation: spin .7s linear infinite;
    margin-bottom: 10px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div class="card">
  <div id="content">
    <div class="loading">
      <div class="spinner"></div>
      <div>Loading server details&#8230;</div>
    </div>
  </div>
</div>

<script type="module">
import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@1.1.2/dist/src/app-with-deps.js";

var app = new App(
  { name: "MCP Advisor Detail", version: "1.0.0" },
  {},
  { autoResize: true }
);

function esc(s) {
  var d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function render(data) {
  var el = document.getElementById("content");

  if (!data || !data.name) {
    el.innerHTML = '<div class="loading">No data available.</div>';
    return;
  }

  var iconHtml;
  if (data.icon_url) {
    iconHtml = '<img src="' + esc(data.icon_url) + '" alt="">';
  } else {
    iconHtml = '&#9881;';
  }

  var stars = data.star_count != null ? data.star_count : (data.stars != null ? data.stars : 0);
  var installs = data.install_count != null ? data.install_count : (data.total_installs != null ? data.total_installs : 0);

  var latestVersion = '';
  var versions = data.versions || [];
  for (var i = 0; i < versions.length; i++) {
    if (versions[i].is_latest) { latestVersion = versions[i].version || ''; break; }
  }

  var html = '';

  /* Header */
  html += '<div class="header">' +
    '<div class="header-icon">' + iconHtml + '</div>' +
    '<div class="header-text">' +
      '<div class="header-title">' + esc(data.title || data.display_name || data.name) + '</div>' +
      '<div class="header-name">' + esc(data.name) + '</div>' +
    '</div>' +
  '</div>';

  /* Description */
  if (data.description) {
    html += '<div class="desc">' + esc(data.description) + '</div>';
  }

  /* Stats */
  html += '<div class="stats">' +
    '<div class="stat-item"><div class="stat-num">' + stars + '</div><div class="stat-label">Stars</div></div>' +
    '<div class="stat-item"><div class="stat-num">' + installs + '</div><div class="stat-label">Installs</div></div>';
  if (latestVersion) {
    html += '<div class="stat-item"><div class="stat-num" style="font-size:14px">' + esc(latestVersion) + '</div><div class="stat-label">Version</div></div>';
  }
  html += '</div>';

  /* Meta */
  var metaHtml = '';
  if (data.repo_url) {
    metaHtml += '<div class="meta-row"><span class="meta-label">Repository</span><span class="meta-value"><a class="meta-link" href="' + esc(data.repo_url) + '" target="_blank">' + esc(data.repo_url) + '</a></span></div>';
  }
  if (data.homepage_url) {
    metaHtml += '<div class="meta-row"><span class="meta-label">Website</span><span class="meta-value"><a class="meta-link" href="' + esc(data.homepage_url) + '" target="_blank">' + esc(data.homepage_url) + '</a></span></div>';
  }
  if (data.created_at) {
    metaHtml += '<div class="meta-row"><span class="meta-label">Published</span><span class="meta-value">' + esc(data.created_at.split("T")[0]) + '</span></div>';
  }
  if (metaHtml) html += '<div class="meta">' + metaHtml + '</div>';

  /* Packages */
  var pkgs = data.packages || [];
  if (pkgs.length > 0) {
    html += '<div class="packages"><div class="packages-title">Install Options</div>';
    for (var p = 0; p < pkgs.length; p++) {
      var pkg = pkgs[p];
      html += '<div class="pkg">' +
        '<span class="pkg-name">' + esc(pkg.package_name || pkg.name || '') + '</span>';
      if (pkg.transport) html += '<span class="badge">' + esc(pkg.transport) + '</span>';
      if (pkg.registry_type) html += '<span class="badge ' + esc(pkg.registry_type) + '">' + esc(pkg.registry_type) + '</span>';
      html += '</div>';
    }
    html += '</div>';
  }

  /* Security */
  if (data.security && data.security.status === 'completed') {
    var sec = data.security;
    var riskClass = 'sec-' + (sec.risk_level || 'none');
    var riskLabel = sec.risk_level === 'none' ? 'No issues found' :
      (sec.risk_level.charAt(0).toUpperCase() + sec.risk_level.slice(1)) + ' risk';
    html += '<div class="security">' +
      '<div class="security-title">Security Scan</div>' +
      '<div class="security-row"><span class="badge ' + riskClass + '">' + esc(riskLabel) + '</span>';
    if (sec.findings_count > 0) {
      html += '<span>' + sec.findings_count + ' finding' + (sec.findings_count !== 1 ? 's' : '') + '</span>';
    }
    if (sec.tools_count > 0) {
      html += '<span>&middot; ' + sec.tools_count + ' tool' + (sec.tools_count !== 1 ? 's' : '') + ' scanned</span>';
    }
    html += '</div>';
    if (sec.scanned_version) {
      html += '<div class="security-row" style="font-size:11px;color:light-dark(#a1a1aa,#71717a)">Scanned version ' + esc(sec.scanned_version) + '</div>';
    }

    /* Individual findings */
    var issues = sec.issues || [];
    if (issues.length > 0) {
      html += '<div class="findings">';
      for (var fi = 0; fi < issues.length; fi++) {
        var issue = issues[fi];
        var sev = (issue.severity || 'low').toLowerCase();
        var typeLabel = (issue.type || 'unknown').replace(/_/g, ' ');
        typeLabel = typeLabel.charAt(0).toUpperCase() + typeLabel.slice(1);
        html += '<div class="finding">' +
          '<div class="finding-icon ' + esc(sev) + '">&#9888;</div>' +
          '<div class="finding-body">' +
            '<div class="finding-type">' + esc(typeLabel) + ' <span class="badge ' + esc('sec-' + sev) + '" style="font-size:9px">' + esc(sev) + '</span></div>';
        if (issue.description) {
          html += '<div class="finding-desc">' + esc(issue.description) + '</div>';
        }
        if (issue.tool) {
          html += '<div class="finding-tool">Tool: ' + esc(issue.tool) + '</div>';
        }
        html += '</div></div>';
      }
      html += '</div>';
    }

    html += '</div>';
  }

  /* Tags */
  var tags = data.tags || [];
  if (tags.length > 0) {
    html += '<div class="tags-section"><div class="tags">';
    for (var t = 0; t < tags.length; t++) {
      html += '<span class="tag">' + esc(tags[t]) + '</span>';
    }
    html += '</div></div>';
  }

  el.innerHTML = html;
}

function showLoading() {
  document.getElementById("content").innerHTML =
    '<div class="loading"><div class="spinner"></div><div>Loading server details&#8230;</div></div>';
}

app.ontoolinput = function() { showLoading(); };

app.ontoolresult = function(result) {
  var data = result.structuredContent;
  if (!data && result.content && result.content[0]) {
    try { data = JSON.parse(result.content[0].text); } catch(e) { data = {}; }
  }
  render(data || {});
};

app.onhostcontextchanged = function(ctx) {
  if (ctx.theme) document.documentElement.style.colorScheme = ctx.theme;
};

await app.connect();
</script>
</body>
</html>
"""
