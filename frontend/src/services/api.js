const DEFAULT_TIMEOUT_MS = 15000;
const API_BASE_URL = (process.env.REACT_APP_API_URL || "").replace(/\/$/, "");

export function buildApiUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

function withTimeout(signal, timeoutMs) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(new Error("timeout")), timeoutMs);

  if (signal) {
    if (signal.aborted) controller.abort(signal.reason);
    else signal.addEventListener("abort", () => controller.abort(signal.reason), { once: true });
  }

  return { signal: controller.signal, cleanup: () => clearTimeout(timeoutId) };
}

async function readResponseBody(res) {
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await res.json();
    } catch {
      return null;
    }
  }
  try {
    return await res.text();
  } catch {
    return null;
  }
}

function getErrorMessage(data, status) {
  if (data && typeof data === "object") {
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => item?.msg || item?.message)
        .filter(Boolean)
        .join(" ");
    }
    if (typeof data.error === "string") return data.error;
    if (typeof data.message === "string") return data.message;
  }
  if (typeof data === "string" && data) return data;
  return `Request failed (${status})`;
}

export class ApiError extends Error {
  constructor(message, { status, url, data } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.url = url;
    this.data = data;
  }
}

export async function apiFetch(
  url,
  { method = "GET", headers, body, signal, timeoutMs, token } = {}
) {
  const timeout = withTimeout(signal, timeoutMs ?? DEFAULT_TIMEOUT_MS);
  const requestUrl = buildApiUrl(url);
  try {
    const res = await fetch(requestUrl, {
      method,
      headers: {
        Accept: "application/json",
        ...(body ? { "Content-Type": "application/json" } : null),
        ...(token ? { Authorization: `Bearer ${token}` } : null),
        ...(headers || null),
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: timeout.signal,
    });

    const data = await readResponseBody(res);

    if (!res.ok) {
      const msg = getErrorMessage(data, res.status);
      throw new ApiError(msg, { status: res.status, url: requestUrl, data });
    }

    return { status: res.status, ok: true, data };
  } finally {
    timeout.cleanup();
  }
}

