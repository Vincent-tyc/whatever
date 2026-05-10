<template>
  <div class="dialogue-container">
    <div class="messages" ref="msgContainer">
      <div v-for="(msg, i) in history" :key="i" :class="['msg', msg.role]">
        <div class="msg-role">{{ msg.role === 'user' ? '&#x1F468;&#x200D;&#x1F3EB; 教师' : '&#x1F916; 系统' }}</div>
        <div class="msg-content">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="msg assistant"><div class="msg-content">思考中...</div></div>
    </div>
    <div class="input-row">
      <input v-model="input" @keyup.enter="send" placeholder="输入反馈或问题..." />
      <button @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { sendDialogue } from '../api.js'

const history = ref([])
const input = ref('')
const loading = ref(false)
const msgContainer = ref(null)

async function send() {
  if (!input.value) return
  loading.value = true
  const res = await sendDialogue(input.value, history.value)
  history.value = res.history
  input.value = ''
  loading.value = false
  await nextTick()
  msgContainer.value?.scrollTo({ top: msgContainer.value.scrollHeight, behavior: 'smooth' })
}
</script>

<style scoped>
.dialogue-container { display: flex; flex-direction: column; height: 400px; }
.messages { flex: 1; overflow-y: auto; margin-bottom: 8px; }
.msg { margin-bottom: 8px; }
.msg-role { font-size: 9px; color: #888; margin-bottom: 2px; }
.msg.user .msg-role { text-align: left; }
.msg.assistant .msg-role { text-align: right; }
.msg-content { background: #0f3460; padding: 8px; border-radius: 6px; font-size: 11px; line-height: 1.5; color: #ccc; }
.msg.assistant .msg-content { background: #1a3a3a; }
.input-row { display: flex; gap: 4px; }
.input-row input {
  flex: 1; padding: 6px 8px; background: #1a1a2e;
  border: 1px solid #0f3460; border-radius: 4px; color: #e0e0e0; font-size: 12px;
}
.input-row button {
  background: #e94560; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;
}
</style>
