<template>
  <section class="page-shell">
    <div class="page-shell__toolbar">
      <button type="button" @click="openCreateDrawer">新增景点</button>
    </div>
    <section class="page-shell__panel">
      <h2>景点列表</h2>
      <ul class="page-shell__list">
        <li v-for="item in spots" :key="item.id">
          <div>
            <strong>{{ item.name }}</strong>
            <p>{{ item.spot_code }} · {{ item.tags.join(' / ') }}</p>
          </div>
          <div class="page-shell__actions">
            <RouterLink :to="`/scenic-spots/${item.id}`">详情</RouterLink>
            <button type="button" @click="openEditDrawer(item)">编辑</button>
          </div>
        </li>
      </ul>
    </section>
    <SpotFormDrawer
      v-model:editing-id="editingId"
      :open="drawerOpen"
      :scenic-areas="scenicAreas"
      :spot="selectedSpot"
      @close="drawerOpen = false"
      @save="handleSave"
    />
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiClient } from '../api/client'
import SpotFormDrawer from '../components/SpotFormDrawer.vue'

type ScenicAreaOption = {
  id: number
  name: string
}

type Spot = {
  id: number
  scenic_area_id: number
  spot_code: string
  name: string
  alias: string | null
  location_text: string | null
  tags: string[]
  open_status: string
}

type SpotFormPayload = Omit<Spot, 'id'> & {
  id?: number
}

const spots = ref<Spot[]>([])
const scenicAreas = ref<ScenicAreaOption[]>([])
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const selectedSpot = ref<Spot | null>(null)

async function loadPage() {
  const [spotsResponse, areasResponse] = await Promise.all([
    apiClient.get('/scenic-spots'),
    apiClient.get('/scenic-areas'),
  ])
  spots.value = spotsResponse.data.items
  scenicAreas.value = areasResponse.data
}

function openCreateDrawer() {
  editingId.value = null
  selectedSpot.value = null
  drawerOpen.value = true
}

function openEditDrawer(spot: Spot) {
  editingId.value = spot.id
  selectedSpot.value = spot
  drawerOpen.value = true
}

async function handleSave(payload: SpotFormPayload) {
  if (payload.id) {
    await apiClient.put(`/scenic-spots/${payload.id}`, payload)
  } else {
    await apiClient.post('/scenic-spots', payload)
  }
  drawerOpen.value = false
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
