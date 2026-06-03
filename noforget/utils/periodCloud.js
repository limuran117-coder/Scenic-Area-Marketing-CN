// utils/periodCloud.js — 姨妈追踪云同步层 v1.0
// 免登录获取openid · 本地优先 · 云端增量同步
// 依赖：wx.cloud.init() 已在 app.js 中初始化

// ─── 本地存储 Key ────────────────────────────────
const LOCAL_OPENID_KEY = 'periodOpenid'
const LOCAL_VERSION_KEY = 'periodCloudVersion'
const LOCAL_SUBSCRIBED_KEY = 'periodSubscribed'
const CURRENT_VERSION = 1

// ─── 云函数名（需在微信云开发控制台部署）───────────
const CLOUD_FUNCTION = 'period-sync'

// ─── 云端集合名（需在云数据库创建）───────────────
const COLLECTION = 'periodData'

// ─── 状态 ───────────────────────────────────────
let _openid = null
let _syncTimer = null
let _pendingSync = false

// ─── 初始化：获取/缓存 openid ──────────────────
function init() {
  _openid = wx.getStorageSync(LOCAL_OPENID_KEY)
  if (_openid) {
    return Promise.resolve(_openid)
  }
  return getOpenidFromCloud()
    .then(openid => {
      _openid = openid
      wx.setStorageSync(LOCAL_OPENID_KEY, openid)
      return openid
    })
    .catch(() => null)
}

// ─── 核心：云函数调用（✅ P0#3修复：自动重试3次）───────
async function callCloud(action, data, retries = 3) {
  if (!_openid && action !== 'whoami') {
    return {success: false, offline: true}
  }

  let lastErr = null
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const res = await wx.cloud.callFunction({
        name: CLOUD_FUNCTION,
        data: {action, data}
      })
      return res.result || {success: false, error: '无返回'}
    } catch (err) {
      lastErr = err
      if (attempt < retries) {
        // 指数退避 + jitter：~1s, ~2s, ~3s
        const delay = attempt * 1000 + Math.round(Math.random() * 500)
        console.warn(`[periodCloud] callCloud(${action}) 第${attempt}次失败，${delay}ms后重试:`, err.message)
        await new Promise(r => setTimeout(r, delay))
      }
    }
  }
  console.error(`[periodCloud] callCloud(${action}) 重试${retries}次后仍然失败:`, lastErr.message)
  return {success: false, error: lastErr.message}
}

// ─── 获取 openid（云函数代理）───────────────────
async function getOpenidFromCloud() {
  const res = await callCloud('whoami', null)
  if (res.success && res.openid) return res.openid
  throw new Error(res.error || '获取openid失败')
}

// ─── 下载云端数据到本地 ─────────────────────────
async function downloadFromCloud() {
  if (!_openid) await init()
  if (!_openid) return null

  const res = await callCloud('get', null)
  if (!res.success || !res.data) return null

  const cloudData = res.data

  if (cloudData.entries) {
    wx.setStorageSync('periodEntries', cloudData.entries)
  }
  if (cloudData.daily) {
    wx.setStorageSync('periodDaily', cloudData.daily)
  }
  if (cloudData.settings) {
    wx.setStorageSync('periodSettings', cloudData.settings)
  }
  if (cloudData.subscribed !== undefined) {
    wx.setStorageSync(LOCAL_SUBSCRIBED_KEY, !!cloudData.subscribed)
  }
  wx.setStorageSync(LOCAL_VERSION_KEY, CURRENT_VERSION)

  return cloudData
}

// ─── 上传本地数据到云端（先拉取合并，避免覆盖其他设备数据）────
async function uploadToCloud(entries, daily, settings) {
  if (!_openid) await init()
  if (!_openid) return false

  // 1. 先从云端拉取（避免直接覆盖其他设备的数据）
  let cloudData = null
  try {
    cloudData = await downloadFromCloud()
  } catch (e) { /* 拉取失败继续上传 */ }

  // 2. 合并：条目取并集（去重），保留最新版本
  const localEntries = entries || wx.getStorageSync('periodEntries') || []
  const cloudEntries = cloudData?.entries || []
  // ✅ P1修复：按 updatedAt 取最新版本，而非先到先得
  const mergedMap = new Map()
  for (const e of [...localEntries, ...cloudEntries]) {
    const key = e.startDate
    const existing = mergedMap.get(key)
    const newTs = e.updatedAt || e.createdAt || 0
    const oldTs = existing ? (existing.updatedAt || existing.createdAt || 0) : 0
    if (!existing || newTs > oldTs) {
      mergedMap.set(key, e)
    }
  }
  const merged = Array.from(mergedMap.values())
  merged.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0))

  const data = {
    version: CURRENT_VERSION,
    entries: merged,
    daily: daily || wx.getStorageSync('periodDaily') || {},
    settings: settings || wx.getStorageSync('periodSettings') || {},
    subscribed: wx.getStorageSync('periodSubscribed') || false,
    uploadedAt: new Date().toISOString()
  }

  // ✅ 容量监控：单文档接近1MB上限时告警
  const dataSize = JSON.stringify(data).length
  if (dataSize > 800000) {
    console.warn(`[periodCloud] ⚠️ 数据接近1MB上限: ${(dataSize / 1024).toFixed(1)}KB for ${_openid}`)
  }

  const res = await callCloud('save', data)
  return res.success
}

// ─── 增量同步（只更新变化的字段）───────────────
async function patchToCloud(changes) {
  if (!_openid) await init()
  if (!_openid) return false

  const res = await callCloud('patch', changes)
  return res.success
}

async function syncSubscribed(subscribed) {
  const nextValue = setSubscribed(subscribed)
  if (!_openid) await init()
  if (!_openid) return false
  return await patchToCloud({subscribed: nextValue})
}

// ─── 定时防抖同步 ───────────────────────────────
function scheduleSync(entries, daily, settings) {
  _pendingSync = true
  if (_syncTimer) clearTimeout(_syncTimer)
  _syncTimer = setTimeout(async () => {
    _pendingSync = false
    _syncTimer = null
    try {
      await uploadToCloud(entries, daily, settings)
    } catch (e) {
      console.error('[periodCloud] scheduleSync failed:', e)
      wx.showToast({ title: '云端同步失败', icon: 'none', duration: 2000 })
    }
  }, 2000)
}

// ─── 一键同步（用户主动触发）───────────────────
async function forceSync() {
  if (_syncTimer) {
    clearTimeout(_syncTimer)
    _syncTimer = null
  }
  if (_pendingSync) {
    const entries = wx.getStorageSync('periodEntries') || []
    const daily = wx.getStorageSync('periodDaily') || {}
    const settings = wx.getStorageSync('periodSettings') || {}
    return await uploadToCloud(entries, daily, settings)
  }
  return true
}

// ─── 检查是否需要数据迁移 ───────────────────────
async function checkMigration() {
  const localVersion = wx.getStorageSync(LOCAL_VERSION_KEY)
  if (localVersion && localVersion !== CURRENT_VERSION) {
    await downloadFromCloud()
    wx.setStorageSync(LOCAL_VERSION_KEY, CURRENT_VERSION)
    return true
  }
  return false
}

// ─── 清除云端身份（退出登录）───────────────────
function clearIdentity() {
  _openid = null
  wx.removeStorageSync(LOCAL_OPENID_KEY)
}

function setSubscribed(subscribed) {
  const nextValue = !!subscribed
  wx.setStorageSync(LOCAL_SUBSCRIBED_KEY, nextValue)
  return nextValue
}

function isSubscribed() {
  return !!wx.getStorageSync(LOCAL_SUBSCRIBED_KEY)
}

// ─── 获取当前状态 ───────────────────────────────
function getStatus() {
  return {
    openid: _openid,
    hasIdentity: !!_openid,
    hasPendingSync: _pendingSync
  }
}

module.exports = {
  init,
  setSubscribed,
  isSubscribed,
  syncSubscribed,
  downloadFromCloud,
  uploadToCloud,
  patchToCloud,
  scheduleSync,
  forceSync,
  checkMigration,
  clearIdentity,
  getStatus
}
