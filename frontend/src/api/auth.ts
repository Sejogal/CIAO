import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, clearTokens, setTokens } from "./client";
import { actions } from "../store";

export type Role = { id: string; name: string; description: string | null } | null;
export type Me = {
  id: string;
  full_name: string;
  email: string;
  avatar: string | null;
  language: string;
  timezone: string;
  is_active: boolean;
  is_verified: boolean;
  role: Role;
  permissions: string[];
};

async function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password });
  const data = await api<{ access_token: string; refresh_token: string }>("/identity/login", {
    method: "POST",
    body,
    skipAuth: true,
  });
  await setTokens(data.access_token, data.refresh_token);
}

async function register(full_name: string, email: string, password: string) {
  await api("/identity/register", {
    method: "POST",
    body: { full_name, email, password },
    skipAuth: true,
  });
}

export function useMe(enabled: boolean) {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => api<Me>("/identity/me"),
    enabled,
    retry: false,
  });
}

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { email: string; password: string }) => {
      await login(vars.email, vars.password);
    },
    onSuccess: () => {
      actions.setLoggedIn(true);
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

export function useRegister() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { name: string; email: string; password: string }) => {
      await register(vars.name, vars.email, vars.password);
      await login(vars.email, vars.password);
    },
    onSuccess: () => {
      actions.setLoggedIn(true);
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return async () => {
    await clearTokens();
    actions.setLoggedIn(false);
    qc.clear();
  };
}
