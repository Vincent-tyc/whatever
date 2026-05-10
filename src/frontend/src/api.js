const BASE = '/api'

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  return res.json()
}

export async function getTextbooks() {
  const res = await fetch(`${BASE}/textbooks`)
  return res.json()
}

export async function buildGraph(textbookId) {
  const res = await fetch(`${BASE}/graph/build/${textbookId}`, { method: 'POST' })
  return res.json()
}

export async function getGraphData() {
  const res = await fetch(`${BASE}/graph/data`)
  return res.json()
}

export async function getGraphForBook(textbookId) {
  const res = await fetch(`${BASE}/graph/data/${textbookId}`)
  return res.json()
}

export async function runIntegration() {
  const res = await fetch(`${BASE}/integration/run`, { method: 'POST' })
  return res.json()
}

export async function getIntegrationStatus() {
  const res = await fetch(`${BASE}/integration/status`)
  return res.json()
}

export async function modifyDecision(decisionId, action, reason) {
  const res = await fetch(`${BASE}/integration/decisions/${decisionId}?action=${action}&reason=${encodeURIComponent(reason)}`, { method: 'POST' })
  return res.json()
}

export async function indexRag() {
  const res = await fetch(`${BASE}/rag/index`, { method: 'POST' })
  return res.json()
}

export async function queryRag(question) {
  const res = await fetch(`${BASE}/rag/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  return res.json()
}

export async function getRagStatus() {
  const res = await fetch(`${BASE}/rag/status`)
  return res.json()
}

export async function sendDialogue(message, history = []) {
  const res = await fetch(`${BASE}/dialogue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history })
  })
  return res.json()
}
