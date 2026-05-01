// pages/index/index.js - 首页逻辑 v2
// 修复：direction丢失 / 使用 getMainCountdown + getElapsedText / 每秒刷新
// 5主题独立视觉：详情页按分类独立，首页按用户主题整体着色
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const themeModule = require('../../utils/theme.js')
const copyTemplates = require('../../utils/copyTemplates.js')
const { getIconPath } = require('../../utils/icons.js')

// 5分类分享卡片配色（与 detail.js 保持一致）
const SHARE_THEME = {
  birthday:       { bg:'#1C0D00', num:'#FFE4B5', sub:'rgba(255,228,181,0.7)',  accent:'#D4A017', emoji:'🎂' },
  love:           { bg:'#1A0515', num:'#FFB6C1', sub:'rgba(255,182,193,0.7)',  accent:'#E8719A', emoji:'💕' },
  wedding:        { bg:'#FFFCF5', num:'#C9A96E', sub:'rgba(139,115,85,0.8)',   accent:'#C9A96E', emoji:'💒' },
  death:          { bg:'#08081A', num:'#C8C8DC', sub:'rgba(200,200,220,0.6)',  accent:'#9090B0', emoji:'🙏', titleColor:'#E0E0EC' },
  pet_birthday:   { bg:'#FFF8F0', num:'#C47830', sub:'rgba(122,72,32,0.8)',   accent:'#C47830', emoji:'🐾', titleColor:'#4A2810' }
}
function getShareTheme(catId) { return SHARE_THEME[catId] || SHARE_THEME.birthday }

/**
 * 将主题颜色对象转成 CSS 变量字符串
 * 用于在 container 的 style 属性中注入
 */
function buildThemeStyle(theme) {
  const vars = []
  if (!theme) return ''
  if (theme.background)    vars.push(`background:${theme.background}`)
  if (theme.textPrimary)    vars.push(`--theme-text-primary:${theme.textPrimary}`)
  if (theme.textSecondary)  vars.push(`--theme-text-secondary:${theme.textSecondary}`)
  if (theme.textAccent)     vars.push(`--theme-text-accent:${theme.textAccent}`)
  if (theme.cardBg)         vars.push(`--theme-card-bg:${theme.cardBg}`)
  if (theme.border)         vars.push(`--theme-border:${theme.border}`)
  if (theme.shadow)        vars.push(`--theme-shadow:${theme.shadow}`)
  if (theme.shadowCard)     vars.push(`--theme-shadow-card:${theme.shadowCard}`)
  return vars.join(';')
}

Page({
  data: {
    statusBarHeight: 20,
    listData: [],
    hasLogin: false,
    userInfo: null,
    showThemePicker: false,
    currentTheme: 'apple',
    theme: {},
    accentColor: '#0066cc',
    themes: [],
    hasMore: false,
    loadingMore: false,
    page: 1,
    pageSize: 20,
    showDailyBanner: false,
    dailyBanner: null
  },

  onLoad() {
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 20,
      themes: themeModule.getAllThemes()
    })
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    const hasLogin = app.globalData.hasLogin
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    const theme = themeModule.getTheme(currentTheme)

    this.setData({
      userInfo, hasLogin,
      currentTheme, theme,
      accentColor: theme.textAccent,
      themeStyle: buildThemeStyle(theme),
      cardBg: theme.cardBg || theme.background || '#ffffff'
    })

    this.loadItems()
    this._startTick()
    this._initDailyBanner()
  },

  // ★ 每日首次温馨话Banner
  _initDailyBanner() {
    if (!this._rawItems || this._rawItems.length === 0) {
      this.setData({ dailyBanner: null, showDailyBanner: false })
      return
    }
    const today = new Date().toDateString()
    const lastDate = wx.getStorageSync('lastBannerDate')
    if (lastDate === today) {
      this.setData({ showDailyBanner: false })
      return
    }
    const topItem = this._rawItems[0]
    const catId = topItem.categoryId || 'default'
    const cat = categories.getCategoryById(catId)
    const elapsed = countdown.getElapsedText(topItem)
    const copy = copyTemplates.getCopy(catId, elapsed.isPast, elapsed.totalDays, elapsed.years)
    const emoji = cat ? cat.icon : '✨'
    this.setData({
      dailyBanner: { text: copy, emoji, catId },
      showDailyBanner: true
    })
    wx.setStorageSync('lastBannerDate', today)
  },

  dismissBanner() {
    this.setData({ showDailyBanner: false })
  },

  onHide() { this._stopTick() },
  onUnload() { this._stopTick() },

  _startTick() {
    this._stopTick()
    this._tickTimer = setInterval(() => {
      this._refreshCountdowns()
    }, 1000)
  },

  _stopTick() {
    if (this._tickTimer) {
      clearInterval(this._tickTimer)
      this._tickTimer = null
    }
  },

  // ★ 每秒刷新：只更新数字，不重新加载/排序
  _refreshCountdowns() {
    if (!this._rawItems || this._rawItems.length === 0) return
    const now = new Date()
    const updated = this._rawItems.map(raw => {
      const main = countdown.getMainCountdown(raw, now)
      return {
        ...this.data.listData.find(d => d.id === raw.id),
        countdownPrecise: main.totalFormatted,
        countdownPreciseDays: main.days,
        countdownHms: (main.totalFormatted.split(' ')[1] || ''),
        preciseIsPast: main.isPast
      }
    })
    this.setData({ listData: updated })
  },

  // ★ 重构 loadItems：使用新的 getMainCountdown + getElapsedText
  loadItems() {
    const localData = wx.getStorageSync('countdownItems') || []
    const now = new Date()

    const processedItems = localData.map(item => {
      // ★ 从 item 本身读取 isRecurring/startDate（不再依赖 categories）
      const itemData = {
        targetDate: item.targetDate,
        isRecurring: item.isRecurring ?? categories.isRecurringCategory(item.categoryId),
        startDate: item.startDate || item.targetDate,
        direction: item.direction
      }

      const main = countdown.getMainCountdown(itemData, now)
      const elapsed = countdown.getElapsedText(itemData, now)

      const cat = categories.getCategoryById(item.categoryId)
      const d = new Date(item.targetDate)
      const dateStr = `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`

      return {
        id: item.id,
        title: item.title,
        dateStr,
        targetDate: item.targetDate,
        isPast: main.isPast,

        // ★ 主倒计时（用于大字）
        countdownPreciseDays: main.days,
        countdownPrecise: main.totalFormatted,
        countdownHms: (main.totalFormatted.split(' ')[1] || ''),
        preciseIsPast: main.isPast,

        // ★ 小字：已过去/已过/还有
        countdownSentence: elapsed.text,

        // ★ isRecurring 透传
        isRecurring: itemData.isRecurring,

        // 保留旧字段（兼容）
        detail: elapsed.text,
        days: main.days,
        icon: cat.icon,
        iconPath: getIconPath(this.data.currentTheme, item.categoryId),
        category: item.categoryId,
        categoryName: cat.name,
        coverImg: item.coverImage || ''
      }
    })

    // ★ 排序：未过的按主倒计时升序，已过的按主倒计时降序
    processedItems.sort((a, b) => {
      if (a.isPast !== b.isPast) return a.isPast ? 1 : -1
      if (!a.isPast) return a.countdownPreciseDays - b.countdownPreciseDays
      return b.countdownPreciseDays - a.countdownPreciseDays
    })

    this.setData({ listData: processedItems, hasMore: processedItems.length >= this.data.pageSize })

    // ★ 保存原始条目（带完整字段），供每秒刷新用
    this._rawItems = localData.map(item => ({
      id: item.id,
      targetDate: item.targetDate,
      isRecurring: item.isRecurring ?? categories.isRecurringCategory(item.categoryId),
      startDate: item.startDate || item.targetDate,
      direction: item.direction,
      categoryId: item.categoryId
    }))
  },

  loadMore() {
    if (!this.data.hasMore || this.data.loadingMore) return
    this.setData({ loadingMore: true })
    setTimeout(() => {
      this.setData({ page: this.data.page + 1, loadingMore: false })
      this.loadItems()
    }, 300)
  },

  onPullDownRefresh() {
    this.loadItems()
    wx.stopPullDownRefresh()
  },

  toggleThemePicker() {
    this.setData({ showThemePicker: !this.data.showThemePicker })
  },

  switchTheme(e) {
    const themeId = e.currentTarget.dataset.theme
    app.setTheme(themeId)
    const theme = themeModule.getTheme(themeId)
    const updatedList = this.data.listData.map(item => ({
      ...item,
      iconPath: getIconPath(themeId, item.category)
    }))
    this.setData({
      currentTheme: themeId, theme,
      listData: updatedList,
      accentColor: theme.textAccent,
      themeStyle: buildThemeStyle(theme),
      cardBg: theme.cardBg || theme.background || '#ffffff',
      showThemePicker: false
    })
  },

  goToAdd() { wx.navigateTo({ url: '/pages/add/add' }) },
  goToDetail(e) { wx.navigateTo({ url: `/pages/detail/detail?id=${e.currentTarget.dataset.id}` }) },
  goToMine() { wx.navigateTo({ url: '/pages/mine/mine' }) },

  shareCard(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.listData.find(i => i.id === id)
    if (!item) return

    wx.showLoading({ title: '生成中...' })
    const ctx = wx.createCanvasContext('shareCanvas')
    const st = getShareTheme(item.category)
    const hasCover = !!(item.coverImg)

    if (hasCover) {
      // ── 有封面图 ──
      ctx.drawImage(item.coverImg, 0, 0, 300, 420)
      ctx.setFillStyle('rgba(0,0,0,0.52)')
      ctx.fillRect(0, 170, 300, 250)
      ctx.setFillStyle('rgba(0,0,0,0.2)')
      ctx.fillRect(0, 0, 300, 65)
    } else {
      // ── 无封面：主题色背景 ──
      ctx.setFillStyle(st.bg)
      ctx.fillRect(0, 0, 300, 420)
    }

    ctx.setTextAlign('center')

    // 顶部标签
    ctx.setFontSize(13)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.9)' : st.accent)
    ctx.fillText(`${st.emoji}  ${item.categoryName || ''}`, 150, 36)

    // 分隔线
    ctx.setStrokeStyle(hasCover ? 'rgba(255,255,255,0.25)' : st.accent)
    ctx.setLineWidth(0.5)
    ctx.setGlobalAlpha(0.3)
    ctx.beginPath()
    ctx.moveTo(80, 52)
    ctx.lineTo(220, 52)
    ctx.stroke()
    ctx.setGlobalAlpha(1)

    // 主数字（衬线字体 Georgia）
    ctx.setFillStyle(hasCover ? '#FFFFFF' : st.num)
    ctx.font = '200 88px Georgia, serif'
    ctx.fillText(item.countdownPreciseDays.toString(), 150, 148)

    // 天标签
    ctx.setFontSize(18)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.75)' : st.sub)
    ctx.font = '300 18px sans-serif'
    ctx.fillText(item.preciseIsPast ? '天已过' : '天', 150, 172)

    // 时分秒
    ctx.setFontSize(18)
    ctx.setGlobalAlpha(0.5)
    const hms = (item.countdownPrecise.split(' ')[1] || '')
    ctx.fillText(hms, 150, 200)
    ctx.setGlobalAlpha(1)

    // 标题
    ctx.setFontSize(22)
    if (hasCover) {
      ctx.setFillStyle('#FFFFFF')
    } else if (item.category === 'death') {
      ctx.setFillStyle('#E0E0EC')
    } else {
      ctx.setFillStyle(st.titleColor || '#FFECD2')
    }
    ctx.font = 'bold 22px sans-serif'
    ctx.fillText(item.title, 150, 248)

    // 日期
    ctx.setFontSize(14)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.7)' : st.sub)
    ctx.font = '14px sans-serif'
    ctx.fillText(item.dateStr, 150, 276)

    // 温馨话
    ctx.setFontSize(13)
    ctx.setFillStyle(hasCover ? 'rgba(255,228,181,0.92)' : st.accent)
    ctx.setGlobalAlpha(0.88)
    ctx.fillText(item.countdownSentence, 150, 328)
    ctx.setGlobalAlpha(1)

    // 底部水印
    ctx.setFontSize(11)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.4)' : st.sub)
    ctx.setGlobalAlpha(0.4)
    ctx.fillText('No Forget · 值得记住的日子', 150, 408)
    ctx.setGlobalAlpha(1)

    ctx.draw(false, () => {
      wx.canvasToTempFilePath({
        canvasId: 'shareCanvas',
        success: (res) => {
          wx.hideLoading()
          wx.showShareImageMenu({ itemList: ['分享给朋友', '分享到朋友圈'], imageUrl: res.tempFilePath })
        },
        fail: () => {
          wx.hideLoading()
          wx.showToast({ title: '生成失败', icon: 'none' })
        }
      })
    })
  }
})
