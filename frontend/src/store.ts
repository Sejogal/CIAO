import { useSyncExternalStore } from "react";

// Empresas, projetos, dispositivos e datastreams passaram a vir da API real
// (ver src/api/*.ts, usado via @tanstack/react-query diretamente nos ecrãs).
// O que fica aqui é só estado que ainda não tem backend (automações,
// notificações - Prioridade 6 do backend, por construir) e preferências
// locais do telemóvel.

export type Automation = { id: string; name: string; datastreamId: string; op: ">" | "<" | "="; threshold: number; action: string; active: boolean };
export type Notice = { id: string; text: string; time: string; level: "warning" | "destructive" | "info"; read: boolean };
export type Prefs = { push: boolean; email: boolean; offline: boolean; theme: "claro" | "escuro" | "sistema"; apiUrl: string };
export type State = { authReady: boolean; loggedIn: boolean; automations: Automation[]; notices: Notice[]; prefs: Prefs; flash: string | null };

const initial: State = {
  authReady: false,
  loggedIn: false,
  automations: [],
  notices: [],
  prefs: { push: true, email: false, offline: true, theme: "claro", apiUrl: "" },
  flash: null,
};

let state = initial;
const listeners = new Set<() => void>();
const notifyListeners = () => listeners.forEach((l) => l());
export const uid = () => Math.random().toString(36).slice(2, 10);
export const setState = (fn: (s: State) => Partial<State>) => {
  state = { ...state, ...fn(state) };
  notifyListeners();
};
export const useStore = () =>
  useSyncExternalStore(
    (l) => (listeners.add(l), () => listeners.delete(l)),
    () => state,
    () => initial,
  );
export const notify = (msg: string) => {
  setState(() => ({ flash: msg }));
  setTimeout(() => setState((s) => (s.flash === msg ? { flash: null } : {})), 2200);
};
const up = <T extends { id: string }>(list: T[], item: T) => (list.some((x) => x.id === item.id) ? list.map((x) => (x.id === item.id ? item : x)) : [...list, item]);

export const actions = {
  setAuthReady: (apiUrl: string, loggedIn: boolean) => setState((s) => ({ authReady: true, loggedIn, prefs: { ...s.prefs, apiUrl } })),
  setLoggedIn: (loggedIn: boolean) => setState(() => ({ loggedIn })),
  saveAutomation: (a: Automation) => setState((s) => ({ automations: up(s.automations, a) })),
  deleteAutomation: (id: string) => setState((s) => ({ automations: s.automations.filter((x) => x.id !== id) })),
  setPrefs: (p: Partial<State["prefs"]>) => setState((s) => ({ prefs: { ...s.prefs, ...p } })),
  readAll: () => setState((s) => ({ notices: s.notices.map((n) => ({ ...n, read: true })) })),
};
