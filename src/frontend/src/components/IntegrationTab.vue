<template>
  <div>
    <div class="stat-cards" v-if="status">
      <div class="stat-card">
        <div class="stat-value">{{ formatSize(status.original_total_chars) }}</div>
        <div class="stat-label">原始总字数</div>
      </div>
      <div class="stat-arrow">&rarr;</div>
      <div class="stat-card">
        <div class="stat-value green">{{ formatSize(status.merged_total_chars) }}</div>
        <div class="stat-label">整合后字数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value orange">{{ (status.compression_ratio * 100).toFixed(1) }}%</div>
        <div class="stat-label">压缩比</div>
      </div>
    </div>

    <button class="action-btn" @click="doIntegrate" :disabled="loading">
      {{ loading ? '整合中...' : '执行跨教材整合' }}
    </button>

    <div class="decision-list" v-if="status?.decisions?.length">
      <h4>整合决策 ({{ status.decisions.length }}项)</h4>
      <div
        v-for="d in status.decisions"
        :key="d.decision_id"
        class="decision-item"
        :class="d.action"
      >
        <div class="decision-top">
          <span class="decision-name">{{ d.result_name }}</span>
          <span class="decision-tag" :class="d.action">{{ actionLabel(d.action) }}</span>
        </div>
        <div class="decision-reason">{{ d.reason }}</div>
        <div class="decision-meta">
          <span>置信度 {{ d.confidence }}</span>
          <span>{{ d.affected_nodes.length }}个节点</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { runIntegration, getIntegrationStatus } from '../api.js'

const status = ref(null)
const loading = ref(false)

async function doIntegrate() {
  loading.value = true
  status.value = await runIntegration()
  loading.value = false
}

function actionLabel(a) {
  return { merge: '合并', keep: '保留', remove: '删除' }[a] || a
}

function formatSize(chars) {
  return chars > 1e6 ? (chars/1e6).toFixed(2)+'MB' : (chars/1e3).toFixed(0)+'KB'
}
</script>

<style scoped>
.stat-cards { display: flex; align-items: center; gap: 6px; margin-bottom: 12px; }
.stat-card { flex: 1; background: #0f3460; border-radius: 8px; padding: 10px; text-align: center; }
.stat-value { font-size: 18px; font-weight: bold; color: #e94560; }
.stat-value.green { color: #00ff88; }
.stat-value.orange { color: #ffaa00; }
.stat-label { font-size: 9px; color: #888; margin-top: 2px; }
.stat-arrow { color: #888; font-size: 18px; }

.action-btn {
  width: 100%; padding: 10px; background: #e94560; color: white;
  border: none; border-radius: 6px; font-size: 13px; cursor: pointer; margin-bottom: 12px;
}
.action-btn:hover { background: #c0392b; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.decision-list { margin-top: 8px; }
.decision-list h4 { font-size: 13px; margin-bottom: 8px; }

.decision-item {
  background: #1a1a2e; border-radius: 6px; padding: 8px; margin-bottom: 4px; border-left: 3px solid #0f3460;
}
.decision-item.merge { border-left-color: #ffaa00; }
.decision-item.keep { border-left-color: #00ff88; }
.decision-item.remove { border-left-color: #e94560; }

.decision-top { display: flex; justify-content: space-between; align-items: center; }
.decision-name { font-size: 12px; font-weight: bold; }
.decision-tag { font-size: 9px; padding: 1px 6px; border-radius: 3px; }
.decision-tag.merge { background: #ffaa00; color: #1a1a2e; }
.decision-tag.keep { background: #00ff88; color: #1a1a2e; }
.decision-tag.remove { background: #e94560; color: white; }

.decision-reason { font-size: 10px; color: #888; margin-top: 4px; }
.decision-meta { display: flex; gap: 10px; font-size: 9px; color: #666; margin-top: 4px; }
</style>
