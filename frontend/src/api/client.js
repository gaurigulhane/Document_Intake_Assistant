const API_BASE = '/api';

export async function createSession() {
  const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function getSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get session');
  return res.json();
}

export async function sendMessage(sessionId, content) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
}

export async function getState(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/state`);
  if (!res.ok) throw new Error('Failed to get state');
  return res.json();
}

export async function updateStateDirectly(sessionId, field, value) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/state`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field, value })
  });
  if (!res.ok) throw new Error('Failed to update state');
  return res.json();
}

export async function getConflicts(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/conflicts`);
  if (!res.ok) throw new Error('Failed to get conflicts');
  return res.json();
}

export async function resolveConflict(sessionId, conflictId, choice) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/conflicts/${conflictId}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ choice })
  });
  if (!res.ok) throw new Error('Failed to resolve conflict');
  return res.json();
}

export async function generateDocument(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/document`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to generate document');
  return res.json();
}

export function getPDFUrl(sessionId) {
  return `${API_BASE}/sessions/${sessionId}/document/pdf`;
}

export async function sendEmail(sessionId, email) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to send email');
  return data;
}
