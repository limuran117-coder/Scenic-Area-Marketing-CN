// pages/index/index.js - 首页逻辑 v2
// 修复：direction丢失 / 使用 getMainCountdown + getElapsedText / 每秒刷新

const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')

// ─── AI文案云端生成（✅ P1#10修复：最大3个并发，避免10个同时触发冷启动）────
const _sloganCache = {}
const _sloganPending = {}
let _sloganConcurrent = 0
const _sloganMaxConcurrent = 3
const _sloganQueue = []

function processSloganQueue() {
  while (_sloganConcurrent < _sloganMaxConcurrent && _sloganQueue.length > 0) {
    const task = _sloganQueue.shift()
    _sloganConcurrent++
    executeSloganTask(task).finally(() => {
      _sloganConcurrent--
      processSloganQueue()
    })
  }
}

async function executeSloganTask(task) {
  const {categoryId, itemId, onDone, cacheKey} = task
  if (_sloganCache[cacheKey]) {
    onDone(_sloganCache[cacheKey])
    return
  }
  const finish = (slogan) => {
    const callbacks = _sloganPending[cacheKey] || []
    delete _sloganPending[cacheKey]
    _sloganCache[cacheKey] = slogan
    callbacks.forEach(cb => cb(slogan))
  }
  if (!wx.cloud || typeof wx.cloud.callFunction !== 'function') {
    finish(categories.pickSubtitle(categoryId))
    return
  }
  try {
    const res = await wx.cloud.callFunction({
      name: 'get-slogan',
      data: {categoryId}
    })
    if (res.result?.success && res.result?.slogan) {
      finish(res.result.slogan)
    } else {
      finish(categories.pickSubtitle(categoryId))
    }
  } catch {
    finish(categories.pickSubtitle(categoryId))
  }
}

function getSloganCacheKey(categoryId, itemId) {
  const today = new Date().toISOString().slice(0, 10)
  return `${categoryId}::${itemId || 'default'}::${today}`
}

function getSloganFromCloud(categoryId, itemId, onDone) {
  const cacheKey = getSloganCacheKey(categoryId, itemId)
  // 命中缓存 → 直接回调
  if (_sloganCache[cacheKey]) {
    onDone(_sloganCache[cacheKey])
    return
  }
  // 已有相同key的请求在pending中 → 加入等待队列
  if (_sloganPending[cacheKey]) {
    _sloganPending[cacheKey].push(onDone)
    return
  }
  _sloganPending[cacheKey] = [onDone]

  // 加入并发队列，等待调度
  _sloganQueue.push({categoryId, itemId, onDone, cacheKey})
  processSloganQueue()
}

const themeModule = require('../../utils/theme.js')
const copyTemplates = require('../../utils/copyTemplates.js')
const {getIconPath} = require('../../utils/icons.js')
const {buildAlmanacSync} = require('../../utils/almanac.js')
const periodUtil = require('../../utils/period.js')
const countdownStore = require('../../utils/countdownStore.js')

function buildThemeStyle(theme) {
  const vars = []
  if (!theme) return ''
  if (theme.background) vars.push(`background:${theme.background}`)
  if (theme.fontFamily) vars.push(`font-family:${theme.fontFamily}`)
  if (theme.textPrimary) vars.push(`--theme-text-primary:${theme.textPrimary}`)
  if (theme.textSecondary) vars.push(`--theme-text-secondary:${theme.textSecondary}`)
  if (theme.textAccent) vars.push(`--theme-text-accent:${theme.textAccent}`)
  if (theme.cardBg) vars.push(`--theme-card-bg:${theme.cardBg}`)
  if (theme.border) vars.push(`--theme-border:${theme.border}`)
  if (theme.shadow) vars.push(`--theme-shadow:${theme.shadow}`)
  if (theme.shadowCard) vars.push(`--theme-shadow-card:${theme.shadowCard}`)
  return vars.join(';')
}

Page({
  data: {
    statusBarHeight: 20,
    navHeight: 64,
    paddingTop: 20,
    listData: [],
    hasPeriodData: false,
    showThemePicker: false,
    currentTheme: 'apple',
    theme: {},
    themes: [],
    hasMore: false,
    loadingMore: false,
    page: 1,
    pageSize: 20,
    scrollIntoView: '',
    showDailyBanner: true,
    dailyBanner: null,
    dailyHuangli: null,
    isRefreshing: false
  },

  onLoad() {
    this.initNavigation()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    const theme = themeModule.getTheme(currentTheme)
    this.setData({
      currentTheme,
      theme,
      themes: themeModule.getAllThemes()
    })
  },

  initNavigation() {
    try {
      const windowInfo = wx.getWindowInfo()
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect()
      const statusBarHeight = windowInfo.statusBarHeight || 20
      const rawNavHeight = menuButtonInfo.bottom + (menuButtonInfo.top - statusBarHeight)
      const navHeight = Math.max(menuButtonInfo.height + 12, rawNavHeight - 8)
      this.setData({
        paddingTop: statusBarHeight,
        statusBarHeight,
        navHeight: Math.round(navHeight),
        totalTopHeight: Math.round(navHeight) + statusBarHeight
      })
    } catch(e) {
      this.setData({paddingTop: 20, navHeight: 64})
    }
  },

  async onShow() {
    try {
      const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
      const theme = themeModule.getTheme(currentTheme)
      const userAvatar = wx.getStorageSync('userAvatar') || ''
      this.setData({
        currentTheme, theme, userAvatar,
        themeStyle: buildThemeStyle(theme),
        page: 1
      })

      // P1-4修复：定期从云端同步（每5分钟一次），持久化跨页面生命周期
      const now = Date.now()
      const lastSync = wx.getStorageSync('_lastCloudSync') || 0
      const needSync = (now - lastSync) > 300000
      if (needSync) wx.setStorageSync('_lastCloudSync', now)
      await this.loadItems({forceRefresh: needSync})

      this._startTick()
      // ✅ P2修复：延迟非首屏计算，不阻塞首页渲染
      setTimeout(() => {
        this._initDailyBanner()
        this._initDailyHuangli()
      }, 100)
      this.refreshAllSlogans()
    } catch(e) {
      console.error('onShow error:', e)
    }
  },

  async onPullDownRefresh() {
    this.setData({isRefreshing: true})
    this.setData({page: 1})
    wx.showLoading({title: '刷新中...', mask: true})
    await this.loadItems({forceRefresh: true})
    wx.hideLoading()
    this.setData({isRefreshing: false})
    wx.stopPullDownRefresh()
  },

  /**
   * ✅ P0#4 修复：banner 跳过周期（period）类型的虚拟条目
   * period 条目在首页展示为姨妈追踪卡片，没有真实 targetDate，
   * 不应参与 banner 文案生成
   */
  _initDailyBanner() {
    if (!this._rawItems || this._rawItems.length === 0) {
      this.setData({dailyBanner: null, showDailyBanner: false})
      return
    }
    const today = new Date().toDateString()
    const lastDate = wx.getStorageSync('lastBannerDate')
    if (lastDate === today) {
      this.setData({showDailyBanner: false})
      return
    }
    // 取第一个非 period 的条目作为 banner
    const topItem = this._rawItems.find(item => item.categoryId !== 'period') || this._rawItems[0]
    const catId = topItem.categoryId || 'default'
    const cat = categories.getCategoryById(catId)
    const elapsed = countdown.getElapsedText(topItem)
    const copy = copyTemplates.getCopy(catId, elapsed.isPast, elapsed.totalDays, elapsed.years)
    const emoji = cat ? cat.icon : '✨'
    this.setData({
      dailyBanner: {text: copy, emoji, catId},
      showDailyBanner: true
    })
    wx.setStorageSync('lastBannerDate', today)
  },

  dismissBanner() { this.setData({showDailyBanner: false}) },

  _initDailyHuangli() {
    const now = new Date()
    const almanac = buildAlmanacSync(now)
    this.setData({
      dailyHuangli: {
        solarDate: almanac.solarDate,
        week: almanac.week,
        lunarFull: almanac.lunarFull,
        yi: Array.isArray(almanac.modernYi) && almanac.modernYi.length ? almanac.modernYi[0] : '记录灵感',
        ji: Array.isArray(almanac.modernJi) && almanac.modernJi.length ? almanac.modernJi[0] : '精神内耗'
      }
    })
  },

  goToAlmanac() { wx.navigateTo({url: '/subpackages/almanac/pages/almanac/almanac'}) },

  goHome() {
    this.setData({scrollIntoView: ''})
    setTimeout(() => this.setData({scrollIntoView: 'top-anchor'}), 0)
  },

  onHide() { this._stopTick() },
  onUnload() { this._stopTick() },

  refreshAllSlogans() {
    const items = this.data.listData
    if (!items) return
    items.forEach((item, idx) => {
      const catId = item.category || item.categoryId
      if (catId === 'period') return
      getSloganFromCloud(catId, item.id || String(idx), slogan => {
        if (this.data.listData[idx]?.cardSubtitle !== slogan) {
          this.setData({[`listData[${idx}].cardSubtitle`]: slogan})
        }
      })
    })
  },

  _startTick() {
    this._stopTick()
    this._tickTimer = setInterval(() => { this._refreshCountdowns() }, 1000)
  },

  _stopTick() {
    if (this._tickTimer) { clearInterval(this._tickTimer); this._tickTimer = null }
  },

  _refreshCountdowns() {
    if (!this._rawItems || this._rawItems.length === 0) return
    const now = new Date()
    const updateData = {}
    let hasChanges = false
    // 只更新时分秒，跳过天数和状态（减少 setData 传输量）
    this._rawItems.forEach((raw, index) => {
      if (raw.categoryId === 'period') return
      const main = countdown.getMainCountdown(raw, now)
      const newHms = (main && main.totalFormatted) ? (main.totalFormatted.split(' ')[1] || '') : ''
      const existing = this.data.listData[index] || {}
      if (existing.countdownHms !== newHms) {
        updateData[`listData[${index}].countdownHms`] = newHms
        hasChanges = true
      }
    })
    if (hasChanges) this.setData(updateData)
  },

  onIconError(e) {
    const idx = parseInt(e.currentTarget.dataset.index)
    const item = this.data.listData[idx]
    if (!item || item.iconLoadError) return
    this.setData({[`listData[${idx}].iconLoadError`]: true})
  },

  async loadItems(options = {}) {
    try {
      const needRefresh = options.forceRefresh || false
      let localData = await countdownStore.getItems({refresh: needRefresh})

      if (!Array.isArray(localData)) {
        localData = []
      }

      const now = new Date()
      const processedItems = []

      for (let i = 0; i < localData.length; i++) {
        const item = localData[i]
        try {
          if (!item || !item.id) continue

          if (item.categoryId === 'period') {
            const entries = periodUtil.getEntries ? periodUtil.getEntries() : []
            const settings = periodUtil.getSettings ? periodUtil.getSettings() : {}
            let prediction = null
            let statusInfo = {mainLabel: '暂无记录', subLabel: '点击记录姨妈', slogan: '好好爱自己，比什么都重要', phase: {key: 'menstruate'}}
            try {
              prediction = periodUtil.predictNext(entries, settings)
              statusInfo = periodUtil.getStatusCardInfo(entries, prediction) || statusInfo
            } catch(e) {}
            const cat = categories.getCategoryById('period')
            let periodDay = null
            let nextDate = null
            const searchStr = (statusInfo.mainLabel || '') + ' ' + (statusInfo.daysInfo || '') + ' ' + (statusInfo.subLabel || '')
            const match = searchStr.match(/第\s*(\d+)\s*天/)
            if (match) periodDay = parseInt(match[1])
            if (prediction && prediction.predictedDate) {
              const d = new Date(prediction.predictedDate)
              nextDate = `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
            }
            const phaseConfigs = {
              menstruate: {name: '姨妈日', icon: '🌸', slogan: '热敷小腹，给自己一个温暖的拥抱 🤗'},
              follicular: {name: '回升期', icon: '🍃', slogan: '身体正在慢慢恢复，状态越来越好啦 ✨'},
              // ✅ P2#25 优化：fertile 阶段用中性表述，避免误解
              fertile: {name: '周期过渡', icon: '☁️', slogan: '身体在悄悄变化，这几天更适合放慢节奏 ☁️'},
              ovulation: {name: '状态高点', icon: '✨', slogan: '今天状态在线，记得把节奏留给自己 🔋'},
              luteal: {name: '暴躁期', icon: '🌧️', slogan: '激素波动可能影响情绪，对自己温柔点 🤍'},
              premenstrual: {name: '下次预警', icon: '⏳', slogan: '姨妈即将来访，记得提前备好小翅膀 🕊️'}
            }
            const phaseKey = (statusInfo.phase && statusInfo.phase.key) || 'menstruate'
            const config = phaseConfigs[phaseKey] || phaseConfigs.menstruate
            processedItems.push({
              id: item.id,
              title: item.title || '姨妈追踪',
              category: 'period',
              isPeriod: true,
              icon: cat.icon || '🌸',
              periodDay,
              statusMain: statusInfo.mainLabel,
              statusSub: statusInfo.daysInfo || statusInfo.subLabel,
              cardSubtitle: statusInfo.slogan || config.slogan,
              nextDate,
              currentPhaseIcon: config.icon,
              currentPhaseName: config.name,
              currentPhaseSlogan: config.slogan,
              isPast: false,
              countdownPreciseDays: 0,
              iconLoadError: false,
              hasPeriodData: !!statusInfo.hasData
            })
            continue
          }

          const cat = categories.getCategoryById(item.categoryId || 'default') || {icon: '✨', name: '默认', isRecurring: false, direction: 'up'}
          const itemData = {
            targetDate: item.targetDate,
            isRecurring: item.isRecurring !== undefined ? item.isRecurring : !!cat.isRecurring,
            startDate: item.startDate || item.targetDate,
            direction: item.direction || cat.direction || 'up'
          }
          const main = countdown.getMainCountdown(itemData, now) || {isPast: false, days: 0, totalFormatted: ''}
          const elapsed = countdown.getElapsedText(itemData, now) || {text: ''}
          const safeDateStr = (item.targetDate || '').replace(/-/g, '/')
          const d = safeDateStr ? new Date(safeDateStr) : new Date()
          processedItems.push({
            id: item.id || Date.now().toString(),
            title: item.title || '未命名',
            dateStr: !isNaN(d.getTime()) ? `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}` : '未知日期',
            targetDate: item.targetDate,
            startDate: itemData.startDate,
            direction: itemData.direction,
            isPast: !!main.isPast,
            countdownPreciseDays: main.days || 0,
            isHugeNumLong: (main.days || 0) >= 10000,
            countdownPrecise: main.totalFormatted || '',
            countdownHms: (main.totalFormatted && main.totalFormatted.split(' ')[1]) || '',
            preciseIsPast: !!main.isPast,
            countdownSentence: elapsed.text || '',
            cardSubtitle: item.cardSubtitle || '满怀期待',
            isRecurring: !!itemData.isRecurring,
            icon: cat.icon || '✨',
            iconPath: getIconPath(this.data.currentTheme, item.categoryId || 'default'),
            iconEmoji: (cat.icon || '✨') + ' ',
            category: item.categoryId || 'default',
            categoryName: cat.name || '默认',
            coverImg: item.coverImage || '',
            iconLoadError: false
          })
        } catch (itemError) {
          console.error('[index] loadItems 单条渲染失败:', item.id, itemError)
        }
      }

      processedItems.sort((a, b) => {
        if (a.isPast !== b.isPast) return a.isPast ? 1 : -1
        if (!a.isPast) return a.countdownPreciseDays - b.countdownPreciseDays
        return b.countdownPreciseDays - a.countdownPreciseDays
      })

      this._allProcessedItems = processedItems
      const visibleCount = this.data.page * this.data.pageSize
      const visibleItems = processedItems.slice(0, visibleCount)

      this.setData({
        listData: visibleItems,
        hasMore: visibleItems.length < processedItems.length
      })

      this._rawItems = processedItems.map(p => ({
        id: p.id,
        targetDate: p.targetDate,
        isRecurring: p.isRecurring,
        startDate: p.startDate,
        direction: p.direction,
        categoryId: p.category
      }))

    } catch (fatalError) {
      console.error('[index] loadItems 加载失败:', fatalError)
    }
  },

  loadMore() {
    if (!this.data.hasMore || this.data.loadingMore) return
    this.setData({loadingMore: true})
    setTimeout(() => {
      const nextPage = this.data.page + 1
      const visibleCount = nextPage * this.data.pageSize
      // ★ 修复：直接切片 _allProcessedItems，避免重新读取存储导致数据不一致
      const allItems = this._allProcessedItems || []
      const visibleItems = allItems.slice(0, visibleCount)
      this.setData({
        page: nextPage,
        loadingMore: false,
        listData: visibleItems,
        hasMore: visibleItems.length < allItems.length
      })
    }, 300)
  },

  goToAdd() { wx.navigateTo({url: '/pages/add/add'}) },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.listData.find(i => i.id === id)
    if (item && item.category === 'period') {
      wx.navigateTo({url: `/pages/period/period?id=${id}`})
      return
    }
    wx.navigateTo({url: `/pages/detail/detail?id=${id}`})
  },

  goToMine() { wx.switchTab({url: '/pages/mine/mine'}) },

  toggleThemePicker() {
    wx.showModal({
      title: '主题',
      content: '当前风格：晨雾莫兰迪',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: 'No Forget - 别忘记重要日子',
      path: '/pages/index/index',
    }
  },

  onShareTimeline: function () {
    return {
      title: 'No Forget - 别忘记重要日子',
    }
  },

  onCopyUrl: function () {
    return {
      query: '',
    }
  }
})