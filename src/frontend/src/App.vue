<template>
  <div class="app-container">
    <header class="app-header">
      <h1>学科知识整合智能体</h1>
      <span class="subtitle">多教材知识图谱 · 跨教材整合 · RAG精准问答</span>
    </header>
    <div class="main-content">
      <LeftPanel class="left-panel"
        @graph-built="onGraphBuilt"
        @integration-done="onIntegrationDone"
        @rag-indexed="onRagIndexed" />
      <GraphView ref="graphView" class="center-panel" />
      <RightPanel ref="rightPanel" class="right-panel" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LeftPanel from './components/LeftPanel.vue'
import GraphView from './components/GraphView.vue'
import RightPanel from './components/RightPanel.vue'

const graphView = ref(null)
const rightPanel = ref(null)

function onGraphBuilt() {
  graphView.value?.loadGraph()
}

function onIntegrationDone() {
  graphView.value?.loadGraph()
  rightPanel.value?.showReport()
}

function onRagIndexed() {
  rightPanel.value?.showRag()
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; }

.app-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a2e;
  color: #e0e0e0;
  overflow: hidden;
}

.app-header {
  height: 48px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 16px;
  flex-shrink: 0;
}

.app-header h1 {
  font-size: 16px;
  color: #e94560;
  white-space: nowrap;
}

.app-header .subtitle {
  font-size: 12px;
  color: #888;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 280px;
  flex-shrink: 0;
  background: #16213e;
  border-right: 1px solid #0f3460;
  overflow-y: auto;
}

.center-panel {
  flex: 1;
  background: #1a1a2e;
  overflow: hidden;
}

.right-panel {
  width: 380px;
  flex-shrink: 0;
  background: #16213e;
  border-left: 1px solid #0f3460;
  overflow-y: auto;
}
</style>
