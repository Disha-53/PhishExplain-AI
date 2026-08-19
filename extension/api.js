const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';
const REQUEST_TIMEOUT_MS = 10000;

async function getApiBaseUrl() {
  const stored = await chrome.storage.local.get('apiBaseUrl');
  return (stored.apiBaseUrl || DEFAULT_API_BASE_URL).replace(/\/$/, '');
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(`${await getApiBaseUrl()}${path}`, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Backend request timed out.');
    }
    throw new Error('Backend is unavailable or blocked by the network policy.');
  } finally {
    clearTimeout(timeout);
  }
  if (!response.ok) {
    throw new Error(`Backend returned HTTP ${response.status}.`);
  }
  try {
    return await response.json();
  } catch {
    throw new Error('Backend returned an invalid JSON response.');
  }
}

async function checkHealth() {
  return request('/health');
}

async function analyzeRequest(payload) {
  return request('/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Backend request failed');
  }

  return response.json();
}
