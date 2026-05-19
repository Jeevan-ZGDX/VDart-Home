export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; status?: number };

export async function apiPostJson<TResponse>(
  path: string,
  body: unknown,
  init?: RequestInit
): Promise<ApiResult<TResponse>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      body: JSON.stringify(body),
      ...init,
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "");
      return {
        ok: false,
        status: res.status,
        error: text || `Request failed (${res.status})`,
      };
    }

    const data = (await res.json()) as TResponse;
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

export async function apiGetJson<TResponse>(
  path: string,
  init?: RequestInit
): Promise<ApiResult<TResponse>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { ...init });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      return {
        ok: false,
        status: res.status,
        error: text || `Request failed (${res.status})`,
      };
    }
    const data = (await res.json()) as TResponse;
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

