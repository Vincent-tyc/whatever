<template>
  <div class="left-panel">
    <h3>教材管理</h3>

    <div
      class="upload-zone"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <div class="upload-icon">+</div>
      <p>拖拽或点击上传</p>
      <p class="hint">PDF / MD / TXT</p>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept=".pdf,.md,.txt"
      multiple
      style="display:none"
      @change="handleFileSelect"
    />

    <div class="textbook-list">
      <div
        v-for="book in textbooks"
        :key="book.id"
        class="textbook-item"
        :class="{ selected: selectedId === book.id }"
        @click="selectBook(book)"
      >
        <div class="book-header">
          <span class="book-icon">{{ iconFor(book.format) }}</span>
          <span class="book-name">{{ book.title }}</span>
        </div>
        <div class="book-meta">
          <span>{{ formatSize(book.size_bytes) }}</span>
          <span class="book-status" :class="book.status">{{ statusText(book.status) }}</span>
        </div>
        <div class="book-actions" v-if="book.status === 'done'">
          <button @click.stop="buildGraph(book.id)">构建图谱</button>
        </div>
      </div>
    </div>

    <div class="global-actions" v-if="textbooks.length >= 2">
      <button class="btn-integrate" @click="handleIntegrate">执行跨教材整合</button>
      <button class="btn-index" @click="handleIndex">建立RAG索引</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadFile, getTextbooks, buildGraph as apiBuildGraph,
         runIntegration, indexRag } from '../api.js'

const textbooks = ref([])
const selectedId = ref(null)
const emit = defineEmits(['select-book', 'graph-built', 'integration-done', 'rag-indexed'])

async function handleFileSelect(e) {
  for (const file of e.target.files) {
    const book = await uploadFile(file)
    textbooks.value.push(book)
  }
}

async function handleDrop(e) {
  for (const file of e.dataTransfer.files) {
    const book = await uploadFile(file)
    textbooks.value.push(book)
  }
}

async function selectBook(book) {
  selectedId.value = book.id
  emit('select-book', book)
}

async function buildGraph(id) {
  await apiBuildGraph(id)
  emit('graph-built', id)
}

async function handleIntegrate() {
  const result = await runIntegration()
  emit('integration-done', result)
}

async function handleIndex() {
  const result = await indexRag()
  emit('rag-indexed', result)
}

function iconFor(format) {
  return ({ pdf: '📄', md: '📝', txt: '📃' })[format] || '📁'
}

function formatSize(bytes) {
  return bytes > 1e6 ? (bytes/1e6).toFixed(1)+' MB' : (bytes/1e3).toFixed(0)+' KB'
}

function statusText(s) {
  return ({ pending: '待解析', parsing: '解析中', done: '已解析', failed: '失败' })[s] || s
}
</script>

<style scoped>
.left-panel { padding: 12px; }
h3 { font-size: 14px; color: #e94560; margin-bottom: 10px; }

.upload-zone {
  border: 2px dashed #e94560;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 12px;
  transition: background 0.2s;
}
.upload-zone:hover { background: rgba(233,69,96,0.1); }
.upload-icon { font-size: 28px; color: #e94560; }
.hint { font-size: 10px; color: #666; margin-top: 4px; }

.textbook-list { display: flex; flex-direction: column; gap: 4px; }
.textbook-item {
  background: #1a1a2e;
  border-radius: 6px;
  padding: 8px 10px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: border-color 0.2s;
}
.textbook-item:hover { border-color: #e94560; }
.textbook-item.selected { border-color: #00ff88; }

.book-header { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.book-icon { font-size: 14px; }
.book-name { font-weight: 600; }
.book-meta { display: flex; justify-content: space-between; font-size: 10px; color: #888; margin-top: 4px; }
.book-status.done { color: #00ff88; }
.book-status.parsing { color: #ffaa00; }

.book-actions { margin-top: 6px; }
.book-actions button {
  background: #0f3460;
  color: #e0e0e0;
  border: none;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}
.book-actions button:hover { background: #e94560; }

.global-actions { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
.btn-integrate, .btn-index {
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 600;
}
.btn-integrate { background: #e94560; color: white; }
.btn-integrate:hover { background: #c0392b; }
.btn-index { background: #0f3460; color: #e0e0e0; }
.btn-index:hover { background: #1a5276; }
</style>
