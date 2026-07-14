const BASE_URL = "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

function buildQuery(params) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  }
  return query.toString();
}

export function syncEmails() {
  return request("/api/sync", { method: "POST" });
}

export function listEmails(filters) {
  return request(`/api/emails?${buildQuery(filters)}`);
}

export function getEmail(id) {
  return request(`/api/emails/${id}`);
}

export function patchEmail(id, patch) {
  return request(`/api/emails/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export function patchEmailsBulk(ids, patch) {
  return request(`/api/emails/bulk`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids, ...patch }),
  });
}

export function getSettings() {
  return request("/api/settings");
}

export function patchSettings(patch) {
  return request("/api/settings", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export function getStats() {
  return request("/api/stats");
}

export function unsubscribeEmail(id) {
  return request(`/api/emails/${id}/unsubscribe`, { method: "POST" });
}

export function exportUrl(filters, ids) {
  const query = buildQuery(ids && ids.length ? { ...filters, ids: ids.join(",") } : filters);
  return `${BASE_URL}/api/export?${query}`;
}
