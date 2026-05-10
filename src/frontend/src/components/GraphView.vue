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
})

async function loadGraph() {
  const data = await getGraphData()
  nodes.value = data.nodes || []
  edges.value = data.edges || []
  textbookCount.value = new Set(nodes.value.map(n => n.textbook_id)).size
  renderChart()
}

function renderChart() {
  if (!chart || nodes.value.length === 0) return

  const graphNodes = nodes.value.map(n => ({
    id: n.id,
    name: n.name,
    symbolSize: Math.min(18 + n.frequency * 10, 60),
    itemStyle: { color: n.color },
    category: n.category,
    data: n
  }))

  const graphEdges = edges.value.map(e => ({
    source: e.source,
    target: e.target,
    lineStyle: {
      color: '#666',
      type: e.relation_type === 'parallel' ? 'dashed' : 'solid',
      width: 1
    }
  }))

  chart.setOption({
    backgroundColor: 'transparent',
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
      force: { repulsion: 300, edgeLength: [100, 250], gravity: 0.1 },
      data: graphNodes,
      edges: graphEdges,
      label: { show: true, fontSize: 9, color: '#ccc' },
      emphasis: { focus: 'adjacency', label: { fontSize: 12 } }
    }]
  })

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

.chart-area { flex: 1; }

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
