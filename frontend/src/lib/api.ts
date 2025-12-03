// Resolve backend base URL.
// Prefer NEXT_PUBLIC_BACKEND_URL, otherwise fall back to current host on port 8000.
const API_BASE =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
    : process.env.NEXT_PUBLIC_BACKEND_URL ||
      `http://${window.location.hostname}:8000`;

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { next: { revalidate: 5 } });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

// Try /api/* first, then fall back to legacy endpoints in this backend.

export async function getEvents() {
  try {
    return await fetchJson<{ events: any[]; total: number }>(
      `${API_BASE}/api/events`,
    );
  } catch {
    // Fallback to existing /events wrapper (force full dataset with limit=0)
    const data = await fetchJson<{ events?: any[]; total?: number }>(
      `${API_BASE}/events?limit=0`,
    );
    if (Array.isArray((data as any).events)) {
      return data as { events: any[]; total: number };
    }
    // Our /events currently returns {"events": [...], "total": n} already
    return data as { events: any[]; total: number };
  }
}

export async function getStats() {
  try {
    return await fetchJson<{
      total_events: number;
      anomalies_detected: number;
      anomaly_rate: number;
      avg_mttd: number;
    }>(`${API_BASE}/api/stats`);
  } catch {
    const m = await fetchJson<{
      metrics: {
        total: number;
        anomalies: number;
        anomalyRate: number;
        avgMttdMinutes: number | null;
      };
    }>(`${API_BASE}/metrics`);
    return {
      total_events: m.metrics.total,
      anomalies_detected: m.metrics.anomalies,
      anomaly_rate: m.metrics.anomalyRate,
      avg_mttd: m.metrics.avgMttdMinutes ?? 0,
    };
  }
}

export async function getUsers() {
  try {
    return await fetchJson<string[]>(`${API_BASE}/api/users`);
  } catch {
    // Derive from events if users endpoint is not available
    const { events } = await getEvents();
    const ids = Array.from(new Set(events.map((e: any) => e.user_id))).sort();
    return ids;
  }
}

export async function getLocations() {
  try {
    return await fetchJson<string[]>(`${API_BASE}/api/locations`);
  } catch {
    const { events } = await getEvents();
    const locs = Array.from(
      new Set(events.map((e: any) => e.location)),
    ).sort();
    return locs;
  }
}

export async function getShap() {
  try {
    return await fetchJson<
      | { features: string[]; importance: number[] }
      | { image: string }
    >(`${API_BASE}/api/shap`);
  } catch {
    // No SHAP endpoint available; return null so UI can show a friendly message
    return null;
  }
}


