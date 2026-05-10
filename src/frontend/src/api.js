const BASE = '/api'

async function parseResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const message = data.detail || data.message || `请求失败 (${res.status})`
    throw new Error(message)
  }
  return data
}

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  return parseResponse(res)
}

export async function getTextbooks() {
  const res = await fetch(`${BASE}/textbooks`)
  return parseResponse(res)
}

export async function buildGraph(textbookId) {
  const res = await fetch(`${BASE}/graph/build/${textbookId}`, { method: 'POST' })
  return parseResponse(res)
}

export async function getGraphBuildStatus(textbookId) {
  const res = await fetch(`${BASE}/graph/build-status/${textbookId}`)
  return parseResponse(res)
}

export async function getGraphData() {
  const res = await fetch(`${BASE}/graph/data`)
  return parseResponse(res)
}

export async function getGraphForBook(textbookId) {
  const res = await fetch(`${BASE}/graph/data/${textbookId}`)
  return parseResponse(res)
}

export async function runIntegration() {
  const res = await fetch(`${BASE}/integration/run`, { method: 'POST' })
  return parseResponse(res)
}

export async function getIntegrationStatus() {
  const res = await fetch(`${BASE}/integration/status`)
  return parseResponse(res)
}

export async function modifyDecision(decisionId, action, reason) {
  const res = await fetch(`${BASE}/integration/decisions/${decisionId}?action=${action}&reason=${encodeURIComponent(reason)}`, { method: 'POST' })
  return parseResponse(res)
}

export async function indexRag() {
  const res = await fetch(`${BASE}/rag/index`, { method: 'POST' })
  return parseResponse(res)
}

export async function queryRag(question) {
  const res = await fetch(`${BASE}/rag/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  return parseResponse(res)
}

export async function getRagStatus() {
  const res = await fetch(`${BASE}/rag/status`)
  return parseResponse(res)
}

export async function sendDialogue(message, history = []) {
  const res = await fetch(`${BASE}/dialogue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history })
  })
  return parseResponse(res)
}
