import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as touristApi from '../api/tourist'
import type { UpdateProfileRequest } from '../types/api'

function normalizeNickname(value: string | null | undefined): string {
  const nickname = (value || '').trim()
  return nickname === '微信用户' ? '' : nickname
}

function normalizeAvatarUrl(value: string | null | undefined): string {
  const avatarUrl = (value || '').trim()
  if (/^(wxfile:\/\/|https?:\/\/tmp\/)/i.test(avatarUrl) || /\/__tmp__\//i.test(avatarUrl)) {
    return ''
  }
  return avatarUrl
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(uni.getStorageSync('token') || '')
  const nickname = ref<string>(normalizeNickname(uni.getStorageSync('wx_nickname') || ''))
  const avatarUrl = ref<string>(normalizeAvatarUrl(uni.getStorageSync('wx_avatar') || ''))
  const visitorDbId = ref<number>(Number(uni.getStorageSync('visitor_db_id')) || 0)
  const isLoggedIn = computed(() => !!token.value && visitorDbId.value > 0)

  function setToken(newToken: string) {
    token.value = newToken
    uni.setStorageSync('token', newToken)
  }

  function setVisitorId(_id: string) {
    // kept for compatibility, no longer used
  }

  function ensureVisitor() {
    // no-op: visitor identity now comes from wx-login
  }

  async function wxLogin(): Promise<boolean> {
    try {
      let code: string

      // #ifdef H5
      uni.showToast({ title: '请在微信小程序中使用微信登录', icon: 'none' })
      return false
      // #endif

      // #ifndef H5
      const loginRes = await new Promise<UniApp.LoginRes>((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: (res) => {
            if (res.code) {
              resolve(res)
              return
            }
            reject(new Error('wx.login did not return code'))
          },
          fail: (err) => reject(err),
        })
      })
      code = loginRes.code
      // #endif

      const data = await touristApi.wxLogin({ code })
      token.value = data.token
      nickname.value = normalizeNickname(data.nickname)
      avatarUrl.value = normalizeAvatarUrl(data.avatar_url)
      visitorDbId.value = data.visitor_id

      uni.setStorageSync('token', data.token)
      uni.setStorageSync('wx_nickname', nickname.value)
      uni.setStorageSync('wx_avatar', avatarUrl.value)
      uni.setStorageSync('visitor_db_id', String(data.visitor_id))
      return true
    } catch (err) {
      console.error('wxLogin failed:', err)
      return false
    }
  }

  async function saveProfile(payload: UpdateProfileRequest): Promise<boolean> {
    try {
      const data = await touristApi.updateProfile(payload)
      nickname.value = normalizeNickname(data.nickname)
      avatarUrl.value = normalizeAvatarUrl(data.avatar_url)
      visitorDbId.value = data.visitor_id

      uni.setStorageSync('wx_nickname', nickname.value)
      uni.setStorageSync('wx_avatar', avatarUrl.value)
      uni.setStorageSync('visitor_db_id', String(data.visitor_id))
      return true
    } catch (err) {
      console.error('saveProfile failed:', err)
      return false
    }
  }

  async function uploadAvatar(filePath: string): Promise<boolean> {
    try {
      const data = await touristApi.uploadAvatar(filePath)
      avatarUrl.value = normalizeAvatarUrl(data.avatar_url)
      visitorDbId.value = data.visitor_id

      uni.setStorageSync('wx_avatar', avatarUrl.value)
      uni.setStorageSync('visitor_db_id', String(data.visitor_id))
      return true
    } catch (err) {
      console.error('uploadAvatar failed:', err)
      return false
    }
  }

  function logout() {
    token.value = ''
    nickname.value = ''
    avatarUrl.value = ''
    visitorDbId.value = 0
    uni.removeStorageSync('token')
    uni.removeStorageSync('wx_nickname')
    uni.removeStorageSync('wx_avatar')
    uni.removeStorageSync('visitor_db_id')
    uni.removeStorageSync('visitor_id')
  }

  return {
    token,
    nickname,
    avatarUrl,
    visitorDbId,
    isLoggedIn,
    setToken,
    setVisitorId,
    ensureVisitor,
    wxLogin,
    saveProfile,
    uploadAvatar,
    logout,
  }
})
