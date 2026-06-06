<template>
  <section class="page-shell">
    <div class="page-shell__toolbar">
      <input v-model="filters.keyword" name="keyword" placeholder="搜索名称/别名/编码" type="search" @keyup.enter="loadPage" />
      <select v-model="filters.open_status" name="open_status" @change="loadPage">
        <option value="">全部状态</option>
        <option value="open">开放</option>
        <option value="closed">关闭</option>
      </select>
      <button type="button" @click="loadPage">搜索</button>
      <button type="button" @click="openCreateDrawer">新增景点</button>
      <button type="button" :disabled="batchLoading" @click="loadBatchCoordinateCandidates">批量扫描待校准</button>
    </div>
    <section class="page-shell__panel">
      <h2>景点列表</h2>
      <ul class="page-shell__list">
        <li v-for="item in spots" :key="item.id">
          <div>
            <strong>{{ item.name }}</strong>
            <p>{{ item.spot_code }} · {{ item.open_status === 'open' ? '开放' : '关闭' }} · {{ item.tags.join(' / ') }}</p>
            <p class="coordinate-status">{{ coordinateStatusText(item) }}</p>
          </div>
          <div class="page-shell__actions">
            <RouterLink :to="`/scenic-spots/${item.id}`">详情</RouterLink>
            <button type="button" @click="openEditDrawer(item)">编辑</button>
            <button
              name="load-coordinate-candidates"
              type="button"
              :disabled="candidateLoading && candidateSpotId === item.id"
              @click="loadCoordinateCandidates(item)"
            >
              腾讯坐标
            </button>
            <button type="button" @click="handleDelete(item.id)">删除</button>
          </div>
        </li>
      </ul>
    </section>
    <section v-if="candidateSpot" class="page-shell__panel coordinate-panel">
      <h2>腾讯地图候选：{{ candidateSpot.name }}</h2>
      <p v-if="candidateSearchKeyword" class="coordinate-status">搜索词：{{ candidateSearchKeyword }}</p>
      <p v-if="candidateError" class="coordinate-error">{{ candidateError }}</p>
      <ul v-if="coordinateCandidates.length" class="page-shell__list">
        <li v-for="candidate in coordinateCandidates" :key="candidateKey(candidate)">
          <div>
            <strong>{{ candidate.title }}</strong>
            <p>{{ candidate.address || '暂无地址' }}</p>
            <p class="coordinate-status">
              {{ formatCoordinate(candidate.latitude) }}，{{ formatCoordinate(candidate.longitude) }}
              · 置信度 {{ candidate.confidence }}
              · 距离 {{ candidate.distance_meters ?? '-' }}m
            </p>
          </div>
          <div class="page-shell__actions">
            <button name="confirm-coordinate-candidate" type="button" @click="confirmCoordinateCandidate(candidate)">
              确认使用
            </button>
          </div>
        </li>
      </ul>
      <p v-else-if="!candidateLoading && !candidateError" class="coordinate-status">暂无候选点位，请手动录入坐标。</p>
    </section>
    <section v-if="coordinateBatchItems.length" class="page-shell__panel coordinate-panel">
      <h2>批量候选结果</h2>
      <ul class="page-shell__list">
        <li v-for="item in coordinateBatchItems" :key="item.spot_id">
          <div>
            <strong>{{ item.spot_name }}</strong>
            <p class="coordinate-status">搜索词：{{ item.search_keyword }}</p>
            <p v-if="!item.candidates.length" class="coordinate-status">暂无候选点位</p>
            <p v-else class="coordinate-status">
              推荐：{{ item.candidates[0].title }} · 置信度 {{ item.candidates[0].confidence }}
            </p>
          </div>
          <div class="page-shell__actions" v-if="item.candidates.length">
            <button type="button" @click="confirmCoordinateCandidate(item.candidates[0], item.spot_id)">
              确认最佳候选
            </button>
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
import { computed, onMounted, reactive, ref } from 'vue'
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
  latitude: number | null
  longitude: number | null
  coordinate_source: string | null
  coordinate_confidence: number | null
  coordinate_verified: boolean
  tencent_poi_id: string | null
  coordinate_address: string | null
  coordinate_raw_json: string | null
  cover_image_url: string | null
  guide_text: string | null
  target_audience: string | null
  parameters_text: string | null
  core_function: string | null
  cultural_value: string | null
  detail_intro: string | null
  highlights: string | null
  performance_info: string | null
  remarks: string | null
  suggested_duration_minutes: number | null
  tags: string[]
  open_status: string
}

type SpotFormPayload = Partial<Omit<Spot, 'id'>> & {
  id?: number
  scenic_area_id: number
  spot_code: string
  name: string
  open_status: string
}

type CoordinateCandidate = {
  provider: string
  title: string
  address: string | null
  category: string | null
  latitude: number
  longitude: number
  confidence: number
  distance_meters: number | null
  tencent_poi_id: string | null
  raw: Record<string, unknown> | null
}

type CoordinateBatchItem = {
  spot_id: number
  spot_name: string
  search_keyword: string
  center: Record<string, number>
  candidates: CoordinateCandidate[]
}

const spots = ref<Spot[]>([])
const scenicAreas = ref<ScenicAreaOption[]>([])
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const selectedSpot = ref<Spot | null>(null)
const candidateSpotId = ref<number | null>(null)
const candidateLoading = ref(false)
const candidateSearchKeyword = ref('')
const coordinateCandidates = ref<CoordinateCandidate[]>([])
const candidateError = ref('')
const batchLoading = ref(false)
const coordinateBatchItems = ref<CoordinateBatchItem[]>([])
const filters = reactive({
  keyword: '',
  open_status: '',
})

async function loadPage() {
  const params = {
    ...(filters.keyword.trim() ? { keyword: filters.keyword.trim() } : {}),
    ...(filters.open_status ? { open_status: filters.open_status } : {}),
  }
  const [spotsResponse, areasResponse] = await Promise.all([
    apiClient.get('/scenic-spots', { params }),
    apiClient.get('/scenic-areas'),
  ])
  spots.value = spotsResponse.data.items
  scenicAreas.value = areasResponse.data
}

const candidateSpot = computed(() => {
  if (candidateSpotId.value == null) return null
  return spots.value.find((item) => item.id === candidateSpotId.value) || null
})

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

async function handleDelete(spotId: number) {
  if (!window.confirm('确认删除该景点？')) return
  await apiClient.delete(`/scenic-spots/${spotId}`)
  await loadPage()
}

function formatCoordinate(value: number | null) {
  return typeof value === 'number' ? value.toFixed(6) : '未录入'
}

function coordinateStatusText(spot: Spot) {
  if (typeof spot.latitude !== 'number' || typeof spot.longitude !== 'number') {
    return '坐标：待校准'
  }
  const source = spot.coordinate_source || 'manual'
  const verified = spot.coordinate_verified ? '已确认' : '待确认'
  const confidence = spot.coordinate_confidence == null ? '' : ` · 置信度 ${spot.coordinate_confidence}`
  return `坐标：${formatCoordinate(spot.latitude)}，${formatCoordinate(spot.longitude)} · ${source} · ${verified}${confidence}`
}

function candidateKey(candidate: CoordinateCandidate) {
  return candidate.tencent_poi_id || `${candidate.latitude},${candidate.longitude}`
}

async function loadCoordinateCandidates(spot: Spot) {
  candidateSpotId.value = spot.id
  candidateLoading.value = true
  candidateError.value = ''
  coordinateCandidates.value = []
  try {
    const response = await apiClient.get(`/scenic-spots/${spot.id}/coordinate-candidates`)
    candidateSearchKeyword.value = response.data.search_keyword
    coordinateCandidates.value = response.data.candidates || []
  } catch {
    candidateError.value = '腾讯地图候选加载失败，请检查后端 TENCENT_MAP_KEY 配置。'
  } finally {
    candidateLoading.value = false
  }
}

async function loadBatchCoordinateCandidates() {
  batchLoading.value = true
  try {
    const response = await apiClient.get('/scenic-spots/coordinate-candidates/batch', {
      params: { only_unverified: true, limit: 50 },
    })
    coordinateBatchItems.value = response.data.items || []
  } finally {
    batchLoading.value = false
  }
}

async function confirmCoordinateCandidate(candidate: CoordinateCandidate, spotId = candidateSpot.value?.id) {
  if (!spotId) return
  await apiClient.post(`/scenic-spots/${spotId}/coordinate-candidates/confirm`, {
    latitude: candidate.latitude,
    longitude: candidate.longitude,
    coordinate_source: candidate.provider,
    coordinate_confidence: candidate.confidence,
    tencent_poi_id: candidate.tencent_poi_id,
    coordinate_address: candidate.address,
    coordinate_raw_json: candidate.raw,
  })
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
