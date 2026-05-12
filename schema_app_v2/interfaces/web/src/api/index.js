/**
 * API helper functions for communicating with the Flask backend
 */

const API_BASE = '/api';

/**
 * Generic API call helper
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} path - API path
 * @param {object} body - Optional request body
 * @returns {Promise<any>} - Parsed JSON response
 */
export async function api(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const r = await fetch(`${API_BASE}${path}`, opts);
  const ct = r.headers.get('content-type') || '';

  if (ct.includes('application/json')) return r.json();
  return { status: 'success', data: await r.text() };
}

/**
 * Schema API helpers
 */
export const schemaApi = {
  create: (sessionId, data) => api('POST', `/schemas/${sessionId}/create`, data),
  delete: (schemaId) => api('DELETE', `/schemas/${schemaId}`),
  get: (schemaId) => api('GET', `/schemas/${schemaId}`),
  save: (schemaId, data) => api('POST', `/schemas/${schemaId}/save`, data),
  list: (library) => api('GET', `/schemas?library=${library}`)
};

/**
 * Component API helpers
 */
export const componentApi = {
  list: (schemaId) => api('GET', `/schemas/${schemaId}/components`),
  add: (schemaId, brickId) => api('POST', `/schemas/${schemaId}/components/${brickId}/add`),
  remove: (schemaId, brickId) => api('DELETE', `/schemas/${schemaId}/components/${brickId}`),
  setParent: (schemaId, brickId, parentData) =>
    api('POST', `/schemas/${schemaId}/components/${brickId}/parent`, parentData),
  removeParent: (schemaId, brickId) =>
    api('DELETE', `/schemas/${schemaId}/components/${brickId}/parent`)
};

/**
 * Schema reference API helpers
 */
export const refApi = {
  list: (schemaId) => api('GET', `/schemas/${schemaId}/refs`),
  add: (schemaId, data) => api('POST', `/schemas/${schemaId}/refs`, data),
  remove: (schemaId, refId) => api('DELETE', `/schemas/${schemaId}/refs/${refId}`)
};

/**
 * Group API helpers
 */
export const groupApi = {
  list: (schemaId) => api('GET', `/schemas/${schemaId}/groups`),
  create: (schemaId, data) => api('POST', `/schemas/${schemaId}/groups`, data),
  delete: (schemaId, groupId) => api('DELETE', `/schemas/${schemaId}/groups/${groupId}`),
  assign: (schemaId, brickId, groupId) =>
    api('POST', `/schemas/${schemaId}/components/${brickId}/group`, { group_id: groupId }),
  remove: (schemaId, brickId) =>
    api('DELETE', `/schemas/${schemaId}/components/${brickId}/group`)
};

/**
 * Tree API helpers
 */
export const treeApi = {
  get: (schemaId) => api('GET', `/schemas/${schemaId}/tree`)
};

/**
 * Brick library API helpers
 */
export const brickApi = {
  listLibraries: () => api('GET', '/bricks/libraries'),
  list: (library) => api('GET', `/bricks?library=${library}`),
  get: (library, brickId) => api('GET', `/bricks/${library}/${brickId}`)
};

/**
 * Session API helpers
 */
export const sessionApi = {
  create: () => api('POST', '/session/create')
};
