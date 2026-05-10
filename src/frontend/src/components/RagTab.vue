<template>
  <div>
    <div class="rag-status" :class="{ ready: status.has_index }">
      {{ status.has_index ? `已索引 ${status.total_chunks || 0} 个知识块，可开始提问` : '尚未建立 RAG 索引' }}
    </div>

    <div class="rag-input-row">
      <input v-model="question" @keyup.enter="askQuestion" placeholder="输入问题..." />
      <button @click="askQuestion">提问</button>
    </div>

    <div class="rag-answer" v-if="answer">
      <div class="answer-text">{{ answer.answer }}</div>
      <div class="citations" v-if="answer.citations?.length">
        <h4>引用来源</h4>
        <div v-for="c in answer.citations" :key="c.textbook + c.chapter" class="citation-item">
          <span>&#x1F4D7; {{ c.textbook }} — {{ c.chapter }} — P.{{ c.page }}</span>
          <span class="score">{{ c.relevance_score?.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { queryRag, getRagStatus } from '../api.js'

const question = ref('')
const answer = ref(null)
const status = ref({})

onMounted(refreshStatus)

async function refreshStatus() {
  status.value = await getRagStatus()
}

async function askQuestion() {
  if (!question.value) return
  answer.value = await queryRag(question.value)
}

defineExpose({ refreshStatus })
</script>

<style scoped>
.rag-status { font-size: 11px; color: #ffaa00; margin-bottom: 8px; }
.rag-status.ready { color: #00ff88; }
.rag-input-row { display: flex; gap: 4px; margin-bottom: 10px; }
.rag-input-row input {
  flex: 1; padding: 6px 8px; background: #1a1a2e;
  border: 1px solid #0f3460; border-radius: 4px; color: #e0e0e0; font-size: 12px;
}
.rag-input-row button {
  background: #e94560; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;
}
.answer-text { background: #1a1a2e; border-radius: 6px; padding: 10px; font-size: 12px; line-height: 1.6; margin-bottom: 8px; color: #ccc; }
.citations h4 { font-size: 11px; color: #888; margin-bottom: 4px; }
.citation-item {
  background: #0f3460; padding: 4px 8px; border-radius: 4px; margin-bottom: 2px;
  display: flex; justify-content: space-between; font-size: 10px; cursor: pointer;
}
.score { color: #00ff88; }
</style>
