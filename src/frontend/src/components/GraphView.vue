<template>
  <div class="graph-container">
    <div class="graph-toolbar">
      <span class="stat">节点: <b>{{ nodes.length }}</b></span>
      <span class="stat">关系: <b>{{ edges.length }}</b></span>
      <span class="stat">教材: <b>{{ textbookCount }}</b></span>
      <input
        v-model="searchText"
        class="search-input"
        placeholder="搜索知识点..."
        @keyup.enter="searchNode"
      />
      <span class="legend-item" v-for="c in legendColors" :key="c.name">
        <span class="dot" :style="{ background: c.color }"></span>{{ c.name }}
      </span>
    </div>

    <div ref="chartDom" class="chart-area"></div>
    <div v-if="emptyMessage" class="empty-message">{{ emptyMessage }}</div>

    <div v-if="selectedNode" class="node-detail-overlay" @click.self="selectedNode = null">
      <div class="node-detail">
        <div class="detail-header">
          <h3>{{ selectedNode.name }}</h3>
          <span class="detail-category">{{ selectedNode.category }}</span>
          <button class="close-btn" @click="selectedNode = null">&times;</button>
        </div>
        <p class="detail-def">{{ selectedNode.definition }}</p>
        <div class="detail-meta">
          <div><label>教材来源</label> <span>{{ selectedNode.textbook_name }}</span></div>
          <div><label>章节</label> <span>{{ selectedNode.chapter }}</span></div>
          <div><label>页码</label> <span>{{ selectedNode.page }}</span></div>
          <div><label>频次</label> <span>{{ selectedNode.frequency }}本教材</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getGraphData } from '../api.js'

const nodes = ref([])
const edges = ref([])
const textbookCount = ref(0)
const searchText = ref('')
const selectedNode = ref(null)
const emptyMessage = ref('暂无图谱数据')
const chartDom = ref(null)
let chart = null

const legendColors = [
  { name: '生理学', color: '#ff6b6b' },
  { name: '病理学', color: '#4ecdc4' },
  { name: '传染病学', color: '#ffe66d' },
  { name: '局部解剖学', color: '#a29bfe' },
  { name: '微生物学', color: '#fd79a8' },
  { name: '病理生理学', color: '#00cec9' },
  { name: '组织学', color: '#fab1a0' }
]

onMounted(() => {
  chart = echarts.init(chartDom.value)
  window.addEventListener('resize', () => chart?.resize())
  loadGraph()
})

async function loadGraph() {
  try {
    emptyMessage.value = '正在加载图谱...'
    const data = await getGraphData()
    nodes.value = data.nodes || []
    edges.value = data.edges || []
    textbookCount.value = new Set(nodes.value.map(n => n.textbook_id)).size
    renderChart()
  } catch (e) {
    nodes.value = []
    edges.value = []
    textbookCount.value = 0
    chart?.clear()
    emptyMessage.value = `图谱加载失败：${e.message}`
  }
}

function renderChart() {
  if (!chart) return

  if (nodes.value.length === 0) {
    chart.clear()
    emptyMessage.value = '暂无图谱数据，请先上传教材并点击构建图谱'
    return
  }

  emptyMessage.value = ''

  // 限制节点数，力导向图超过50个节点布局计算极慢
  const MAX_DISPLAY = 50
  const seenIds = new Set()
  const displayNodes = nodes.value
    .filter(n => n?.id && !seenIds.has(n.id) && seenIds.add(n.id))
    .slice(0, MAX_DISPLAY)
  const displayNodeIds = new Set(displayNodes.map(n => n.id))
  const nodeNameById = new Map(displayNodes.map(n => [n.id, n.name]))
  const displayEdges = edges.value.filter(
    e => e?.source && e?.target && displayNodeIds.has(e.source) && displayNodeIds.has(e.target)
  )

  const graphNodes = displayNodes.map(n => ({
    id: String(n.id),
    name: n.name,
    symbolSize: Math.min(18 + n.frequency * 10, 60),
    itemStyle: { color: n.color },
    category: n.category,
    data: n
  }))

  const graphEdges = displayEdges.map((e, index) => ({
    id: `${e.source}->${e.target}-${index}`,
    source: nodeNameById.get(e.source),
    target: nodeNameById.get(e.target),
    lineStyle: {
      color: e.relation_type === 'parallel' ? 'rgba(148, 163, 184, 0.9)' : 'rgba(125, 211, 252, 0.95)',
      type: e.relation_type === 'parallel' ? 'dashed' : 'solid',
      width: e.relation_type === 'parallel' ? 1.6 : 2.2,
      opacity: 0.9
    }
  }))

  const connectedNodeNames = new Set()
  graphEdges.forEach(edge => {
    connectedNodeNames.add(edge.source)
    connectedNodeNames.add(edge.target)
  })

  const supplementalEdges = []
  for (let i = 1; i < graphNodes.length; i++) {
    const prev = graphNodes[i - 1]
    const current = graphNodes[i]
    if (!connectedNodeNames.has(current.name) || graphEdges.length === 0) {
      supplementalEdges.push({
        id: `supplemental-${i}`,
        source: prev.name,
        target: current.name,
        silent: true,
        lineStyle: {
          color: 'rgba(148, 163, 184, 0.35)',
          type: 'dotted',
          width: 1,
          opacity: 0.55
        }
      })
    }
  }

  chart.clear()
  chart.setOption({
    backgroundColor: '#111827',
    animation: false,
    tooltip: {
      formatter: (p) => {
        if (p.dataType === 'node') {
          const d = p.data.data
          return `<b>${d.name}</b><br/>${d.definition?.slice(0,80)}...<br/>${d.textbook_name} · ${d.chapter}`
        }
        return ''
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      force: { repulsion: 200, edgeLength: [80, 200], gravity: 0.05, layoutAnimation: false },
      data: graphNodes,
      edges: [...graphEdges, ...supplementalEdges],
      label: {
        show: true,
        fontSize: 10,
        color: '#f8fafc',
        textBorderColor: '#111827',
        textBorderWidth: 3
      },
      emphasis: { focus: 'adjacency', label: { fontSize: 12 } }
    }]
  })

  chart.resize()

  chart.off('click')
  chart.on('click', (params) => {
    if (params.dataType === 'node' && params.data?.data) {
      selectedNode.value = params.data.data
    } else {
      selectedNode.value = null
    }
  })
}

function searchNode() {
  if (!chart || !searchText.value) return
  chart.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  chart.dispatchAction({
    type: 'highlight',
    seriesIndex: 0,
    name: searchText.value
  })
}

watch(() => nodes.value.length, () => nextTick(renderChart))

defineExpose({ loadGraph })
</script>

<style scoped>
.graph-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.graph-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #0f3460;
  font-size: 11px;
  flex-shrink: 0;
}

.stat { color: #aaa; }
.stat b { color: #fff; }

.search-input {
  margin-left: auto;
  width: 160px;
  padding: 4px 8px;
  background: #1a1a2e;
  border: 1px solid #0f3460;
  border-radius: 4px;
  color: #e0e0e0;
  font-size: 11px;
}

.legend-item { display: flex; align-items: center; gap: 4px; font-size: 10px; color: #888; }
.legend-item .dot { width: 8px; height: 8px; border-radius: 50%; }

.chart-area { flex: 1; min-height: 400px; width: 100%; background: #111827; }

.empty-message {
  position: absolute;
  inset: 44px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 13px;
  pointer-events: none;
}

.node-detail-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.node-detail {
  background: #16213e;
  border-radius: 12px;
  padding: 20px;
  width: 400px;
  max-height: 80%;
  overflow-y: auto;
}

.detail-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.detail-header h3 { color: #fff; font-size: 18px; }
.detail-category { background: #e94560; color: white; padding: 2px 10px; border-radius: 10px; font-size: 11px; }
.close-btn { margin-left: auto; background: none; border: none; color: #888; font-size: 22px; cursor: pointer; }

.detail-def { color: #ccc; line-height: 1.6; font-size: 13px; margin-bottom: 12px; }
.detail-meta div { display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px; border-bottom: 1px solid #0f3460; }
.detail-meta label { color: #888; }
.detail-meta span { color: #e0e0e0; }
</style>
