<template>
  <div>
    <div class="report-section" v-if="status">
      <h4>整合概览</h4>
      <table class="report-table">
        <tbody>
          <tr><td>原始教材数</td><td>{{ textbookCount }}本</td></tr>
          <tr><td>原始总字数</td><td>{{ formatSize(status.original_total_chars) }}</td></tr>
          <tr><td>整合后字数</td><td class="green">{{ formatSize(status.merged_total_chars) }}</td></tr>
          <tr><td>压缩比</td><td class="orange">{{ (status.compression_ratio * 100).toFixed(1) }}%</td></tr>
          <tr><td>整合决策</td><td>合并{{ mergeCount }}项 · 保留{{ keepCount }}项 · 删除{{ removeCount }}项</td></tr>
        </tbody>
      </table>
    </div>

    <div v-if="!status" class="empty">尚未执行整合，请先在「整合操作」Tab中执行</div>

    <button class="export-btn" @click="exportReport" :disabled="!status">导出 Markdown 报告</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getIntegrationStatus, getTextbooks } from '../api.js'

const status = ref(null)
const textbookCount = ref(0)

onMounted(refreshStatus)

async function refreshStatus() {
  try { status.value = await getIntegrationStatus() } catch { status.value = null }
  const books = await getTextbooks()
  textbookCount.value = books.length
}

const mergeCount = computed(() => status.value?.decisions?.filter(d => d.action === 'merge').length || 0)
const keepCount = computed(() => status.value?.decisions?.filter(d => d.action === 'keep').length || 0)
const removeCount = computed(() => status.value?.decisions?.filter(d => d.action === 'remove').length || 0)

function formatSize(chars) {
  return chars > 1e6 ? (chars/1e6).toFixed(2)+' MB' : (chars/1e3).toFixed(0)+' KB'
}

function exportReport() {
  if (!status.value) return
  const lines = [
    '# 学科知识整合报告', '',
    '## 整合概览',
    `- 原始教材数量：${textbookCount.value} 本`,
    `- 原始总字数：${formatSize(status.value.original_total_chars)}`,
    `- 整合后字数：${formatSize(status.value.merged_total_chars)}`,
    `- 压缩比：${(status.value.compression_ratio * 100).toFixed(1)}%`,
    '', '## 整合决策摘要',
    `- 合并：${mergeCount.value} 项`,
    `- 保留：${keepCount.value} 项`,
    `- 删除：${removeCount.value} 项`,
    '', '## 重点整合案例',
    ...status.value.decisions.slice(0, 5).map(d =>
      `- **${d.result_name}** (${d.action})：${d.reason}（置信度 ${d.confidence}）`
    )
  ]
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = '整合报告.md'; a.click()
}

defineExpose({ refreshStatus })
</script>

<style scoped>
.report-section { margin-bottom: 12px; }
.report-section h4 { font-size: 13px; margin-bottom: 8px; }
.report-table { width: 100%; font-size: 11px; border-collapse: collapse; }
.report-table td { padding: 4px 0; border-bottom: 1px solid #0f3460; }
.report-table td:last-child { text-align: right; }
.green { color: #00ff88; }
.orange { color: #ffaa00; }
.empty { color: #888; font-size: 12px; padding: 20px 0; text-align: center; }
.export-btn {
  width: 100%; padding: 10px; background: #0f3460; color: #e0e0e0;
  border: none; border-radius: 6px; font-size: 13px; cursor: pointer; margin-top: 8px;
}
.export-btn:hover { background: #1a5276; }
.export-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
