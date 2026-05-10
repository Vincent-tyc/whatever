<template>
  <div class="right-panel">
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </div>
    <div class="tab-content">
      <IntegrationTab v-if="activeTab === 'integration'" />
      <RagTab v-else-if="activeTab === 'rag'" ref="ragTab" />
      <DialogueTab v-else-if="activeTab === 'dialogue'" />
      <ReportTab v-else ref="reportTab" />
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import IntegrationTab from './IntegrationTab.vue'
import RagTab from './RagTab.vue'
import DialogueTab from './DialogueTab.vue'
import ReportTab from './ReportTab.vue'

const activeTab = ref('integration')
const ragTab = ref(null)
const reportTab = ref(null)
const tabs = [
  { id: 'integration', label: '整合操作' },
  { id: 'rag', label: 'RAG问答' },
  { id: 'dialogue', label: '对话' },
  { id: 'report', label: '报告' }
]

async function showRag() {
  activeTab.value = 'rag'
  await nextTick()
  await ragTab.value?.refreshStatus()
}

async function showReport() {
  activeTab.value = 'report'
  await nextTick()
  await reportTab.value?.refreshStatus()
}

defineExpose({ showRag, showReport })
</script>

<style scoped>
.right-panel { display: flex; flex-direction: column; height: 100%; }
.tab-bar {
  display: flex;
  border-bottom: 1px solid #0f3460;
  flex-shrink: 0;
}
.tab-bar button {
  flex: 1;
  padding: 8px 4px;
  background: none;
  border: none;
  color: #888;
  font-size: 11px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab-bar button.active {
  color: #e94560;
  border-bottom-color: #e94560;
}
.tab-bar button:hover { color: #e0e0e0; }
.tab-content { flex: 1; overflow-y: auto; padding: 12px; }
</style>
