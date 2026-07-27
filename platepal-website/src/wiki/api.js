// Thin fetch wrapper for the recipe wiki API.
// The access token lives only in memory; the refresh token is an httpOnly
// cookie handled by the browser. On a 401 we transparently try one refresh.

const BASE = '/wiki-api';

let accessToken = null;
let challengeToken = null;
let refreshPromise = null;

export function setAccessToken(token) {
  accessToken = token || null;
}

export function getAccessToken() {
  return accessToken;
}

// The challenge token proves the password step passed and authorises the
// first-login setup steps (password change, TOTP setup) and the 2FA step.
// It lives only in memory and is cleared once a full session is issued.
export function setChallengeToken(token) {
  challengeToken = token || null;
}

function buildHeaders(extra, hasBody, useChallenge) {
  const headers = { ...(extra || {}) };
  if (hasBody) headers['Content-Type'] = 'application/json';
  const token = useChallenge ? challengeToken : accessToken;
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function parseError(res) {
  let detail = res.statusText;
  try {
    const data = await res.json();
    if (data && data.detail) {
      detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg || d).join(', ')
        : data.detail;
    }
  } catch {
    /* non-JSON error body */
  }
  const err = new Error(detail);
  err.status = res.status;
  return err;
}

async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    })
      .then(async (res) => {
        if (!res.ok) throw await parseError(res);
        const data = await res.json();
        setAccessToken(data.access_token);
        return data.access_token;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

async function request(path, { method = 'GET', body, auth = false, challenge = false, retry = true } = {}) {
  const hasBody = body !== undefined;
  const res = await fetch(`${BASE}${path}`, {
    method,
    credentials: 'include',
    headers: buildHeaders(undefined, hasBody, challenge),
    body: hasBody ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth && retry) {
    try {
      await refreshAccessToken();
    } catch {
      throw await parseError(res);
    }
    return request(path, { method, body, auth, retry: false });
  }

  if (!res.ok) throw await parseError(res);
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  request,
  refreshAccessToken,

  // Public reads
  listRecipes: (locale, q) =>
    request(`/recipes?locale=${encodeURIComponent(locale)}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  getRecipe: (slug, locale) => request(`/recipes/${encodeURIComponent(slug)}?locale=${encodeURIComponent(locale)}`),
  exportRecipe: (slug, locale, portion = 'serving') =>
    request(
      `/recipes/${encodeURIComponent(slug)}/export?locale=${encodeURIComponent(locale)}&portion=${encodeURIComponent(portion)}`,
    ),
  listIngredients: (locale, q) =>
    request(`/ingredients?locale=${encodeURIComponent(locale)}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  getIngredient: (slug, locale) =>
    request(`/ingredients/${encodeURIComponent(slug)}?locale=${encodeURIComponent(locale)}`),
  imageUrl: (id) => (id ? `${BASE}/images/${id}` : null),
  absoluteImageUrl: (id) => (id ? `${window.location.origin}${BASE}/images/${id}` : null),

  // Auth
  login: async (username, password) => {
    const res = await request('/auth/login', { method: 'POST', body: { username, password } });
    setChallengeToken(res.challenge_token);
    return res;
  },
  challengePassword: async (new_password) => {
    const res = await request('/auth/challenge/password', { method: 'POST', body: { new_password }, challenge: true });
    setChallengeToken(res.challenge_token);
    return res;
  },
  totpInit: () => request('/auth/challenge/totp/init', { method: 'POST', challenge: true }),
  totpVerify: (code) => request('/auth/challenge/totp/verify', { method: 'POST', body: { code }, challenge: true }),
  mfa: (code) => request('/auth/mfa', { method: 'POST', body: { code }, challenge: true }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me', { auth: true }),
  regenerateRecovery: () => request('/auth/recovery/regenerate', { method: 'POST', auth: true }),

  // Admin content
  uploadImage: (data) => request('/images', { method: 'POST', body: { data }, auth: true }),
  adminListIngredients: () => request('/admin/ingredients', { auth: true }),
  adminGetIngredient: (id) => request(`/admin/ingredients/${id}`, { auth: true }),
  createIngredient: (payload) => request('/admin/ingredients', { method: 'POST', body: payload, auth: true }),
  updateIngredient: (id, payload) => request(`/admin/ingredients/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteIngredient: (id) => request(`/admin/ingredients/${id}`, { method: 'DELETE', auth: true }),
  adminListRecipes: () => request('/admin/recipes', { auth: true }),
  adminGetRecipe: (id) => request(`/admin/recipes/${id}`, { auth: true }),
  createRecipe: (payload) => request('/admin/recipes', { method: 'POST', body: payload, auth: true }),
  updateRecipe: (id, payload) => request(`/admin/recipes/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteRecipe: (id) => request(`/admin/recipes/${id}`, { method: 'DELETE', auth: true }),
};
