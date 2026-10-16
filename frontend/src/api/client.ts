import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "ciao_access_token";
const REFRESH_KEY = "ciao_refresh_token";
const API_URL_KEY = "ciao_api_url";
export const DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1";

let apiUrl = DEFAULT_API_URL;
let accessToken: string | null = null;
let refreshToken: string | null = null;

export async function loadAuthFromStorage() {
  const [url, at, rt] = await Promise.all([
    SecureStore.getItemAsync(API_URL_KEY),
    SecureStore.getItemAsync(TOKEN_KEY),
    SecureStore.getItemAsync(REFRESH_KEY),
  ]);
  if (url) apiUrl = url;
  accessToken = at;
  refreshToken = rt;
  return { apiUrl, loggedIn: !!accessToken };
}

export async function setApiUrl(url: string) {
  apiUrl = url;
  await SecureStore.setItemAsync(API_URL_KEY, url);
}
export const getApiUrl = () => apiUrl;

export async function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  await Promise.all([
    SecureStore.setItemAsync(TOKEN_KEY, access),
    SecureStore.setItemAsync(REFRESH_KEY, refresh),
  ]);
}

export async function clearTokens() {
  accessToken = null;
  refreshToken = null;
  await Promise.all([
    SecureStore.deleteItemAsync(TOKEN_KEY),
    SecureStore.deleteItemAsync(REFRESH_KEY),
  ]);
}

export const isLoggedIn = () => !!accessToken;

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  if (!refreshToken) return false;
  if (refreshing) return refreshing;
  refreshing = (async () => {
    try {
      const res = await fetch(`${apiUrl}/identity/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      await setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

/** skipAuth: para login/registo, onde ainda não há token. */
export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown; skipAuth?: boolean; retried?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  const isForm = options.body instanceof URLSearchParams;
  // O fetch do React Native, ao contrário do browser, não define o Content-Type
  // sozinho para um body URLSearchParams - sem isto o FastAPI não reconhece os
  // campos como form data e rejeita com 422.
  headers["Content-Type"] = isForm ? "application/x-www-form-urlencoded" : "application/json";
  if (!options.skipAuth && accessToken) headers.Authorization = `Bearer ${accessToken}`;

  const res = await fetch(`${apiUrl}${path}`, {
    method: options.method ?? "GET",
    headers,
    body:
      options.body === undefined
        ? undefined
        : isForm
          ? (options.body as URLSearchParams).toString()
          : JSON.stringify(options.body),
  });

  if (res.status === 204) return undefined as T;

  if (res.status === 401 && !options.skipAuth && !options.retried) {
    const refreshed = await tryRefresh();
    if (refreshed) return api<T>(path, { ...options, retried: true });
  }

  if (!res.ok) {
    const payload = await res.json().catch(() => null);
    const message =
      (payload && typeof payload.detail === "string" && payload.detail) ||
      (payload && Array.isArray(payload.detail) && payload.detail[0]?.msg) ||
      `Erro ${res.status}`;
    throw new ApiError(message, res.status);
  }

  return res.json().catch(() => undefined as T);
}
