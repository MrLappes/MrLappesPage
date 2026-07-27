// Reactive admin auth store for the recipe wiki.
import { reactive } from 'vue';
import { api, setAccessToken } from './api.js';

export const auth = reactive({
  isAuthenticated: false,
  username: null,
  ready: false, // true once the initial silent refresh has resolved
});

// Attempt a silent refresh on app start so a returning admin stays logged in.
export async function initAuth() {
  try {
    await api.refreshAccessToken();
    const me = await api.me();
    auth.isAuthenticated = true;
    auth.username = me.username;
  } catch {
    auth.isAuthenticated = false;
    auth.username = null;
  } finally {
    auth.ready = true;
  }
}

export function completeLogin(session) {
  setAccessToken(session.access_token);
  auth.isAuthenticated = true;
  auth.username = session.username;
}

export async function logout() {
  try {
    await api.logout();
  } catch {
    /* ignore */
  }
  setAccessToken(null);
  auth.isAuthenticated = false;
  auth.username = null;
}
