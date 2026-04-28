import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  intent?: string
  loading?: boolean
  timestamp: number
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const sessionId = ref<number | null>(null)
  const isGenerating = ref(false)

  function addUserMessage(content: string) {
    messages.value.push({
      id: `u_${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now(),
    })
  }

  function addAssistantPlaceholder(): string {
    const id = `a_${Date.now()}`
    messages.value.push({
      id,
      role: 'assistant',
      content: '',
      loading: true,
      timestamp: Date.now(),
    })
    return id
  }

  function updateAssistantMessage(id: string, content: string, intent?: string) {
    const msg = messages.value.find((m) => m.id === id)
    if (msg) {
      msg.content = content
      msg.intent = intent
      msg.loading = false
    }
  }

  function appendToMessage(id: string, chunk: string) {
    const msg = messages.value.find((m) => m.id === id)
    if (msg) {
      msg.content += chunk
    }
  }

  function setSessionId(id: number) {
    sessionId.value = id
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = null
  }

  return {
    messages,
    sessionId,
    isGenerating,
    addUserMessage,
    addAssistantPlaceholder,
    updateAssistantMessage,
    appendToMessage,
    setSessionId,
    clearMessages,
  }
})
