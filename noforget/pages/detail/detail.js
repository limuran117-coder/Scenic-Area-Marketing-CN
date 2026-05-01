// pages/detail/detail.js - 详情页逻辑 v2
// 修复：使用 getMainCountdown + getElapsedText 计算完整数据
// 分享卡片：按分类独立主题色绘制
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const copyTemplates = require('../../utils/copyTemplates.js')

// 5分类的分享卡片配色
const SHARE_THEME = {
  birthday: {
    bg: '#1C0D00', numColor: '#FFE4B5', labelColor: 'rgba(255,228,181,0.7)',
    titleColor: '#FFECD2', subColor: 'rgba(255,220,170,0.7)',
    accentColor: '#D4A017', emoji: '🎂'
  },
  love: {
    bg: '#1A0515', numColor: '#FFB6C1', labelColor: 'rgba(255,182,193,0.7)',
    titleColor: '#FFDDE5', subColor: 'rgba(255,200,210,0.7)',
    accentColor: '#E8719A', emoji: '💕'
  },
  wedding: {
    bg: '#FFFCF5', numColor: '#C9A96E', labelColor: 'rgba(139,115,85,0.7)',
    titleColor: '#2D2D2D', subColor: 'rgba(139,115,85,0.8)',
    accentColor: '#C9A96E', emoji: '💒'
  },
  death: {
    bg: '#08081A', numColor: '#C8C8DC', labelColor: 'rgba(200,200,220,0.6)',
    titleColor: '#E0E0EC', subColor: 'rgba(200,200,220,0.65)',
    accentColor: '#9090B0', emoji: '🙏'
  },
  pet_birthday: {
    bg: '#FFF8F0', numColor: '#C47830', labelColor: 'rgba(122,72,32,0.7)',
    titleColor: '#4A2810', subColor: 'rgba(122,72,32,0.8)',
    accentColor: '#C47830', emoji: '🐾'
  }
}

function getShareTheme(categoryId) {
  return SHARE_THEME[categoryId] || SHARE_THEME.birthday
}

Page({
  data: {
    statusBarHeight: 20,
    item: null,
    theme: {},
    currentTheme: 'apple',
    remindEnabled: false,
    id: null
  },

  onLoad(options) {
    const systemInfo = wx.getSystemInfoSync()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 20,
      currentTheme,
      theme: app.globalData.themes[currentTheme],
      id: options.id
    })
  },

  onShow() {
    this.loadItem()
    this._startTick()
  },

  onHide() { this._stopTick() },
  onUnload() { this._stopTick() },

  _startTick() {
    this._stopTick()
    this._tickTimer = setInterval(() => { this._refreshCountdown() }, 1000)
  },

  _stopTick() {
    if (this._tickTimer) { clearInterval(this._tickTimer); this._tickTimer = null }
  },

  _refreshCountdown() {
    const item = this.data.item
    if (!item) return
    const main = countdown.getMainCountdown({
      targetDate: item.targetDate,
      isRecurring: item.isRecurring,
      direction: item.direction
    })
    this.setData({
      item: {
        ...item,
        countdownPrecise: main.totalFormatted,
        countdownHms: (main.totalFormatted.split(' ')[1] || ''),
        countdownPreciseDays: main.days,
        preciseIsPast: main.isPast
      }
    })
  },

  loadItem() {
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    const items = wx.getStorageSync('countdownItems') || []
    const raw = items.find(i => i.id === this.data.id)

    if (!raw) {
      wx.showToast({ title: '未找到', icon: 'none' })
      setTimeout(() => { wx.navigateBack() }, 1000)
      return
    }

    const now = new Date()
    const cat = categories.getCategoryById(raw.categoryId)

    const itemData = {
      targetDate: raw.targetDate,
      isRecurring: raw.isRecurring ?? categories.isRecurringCategory(raw.categoryId),
      startDate: raw.startDate || raw.targetDate,
      direction: raw.direction || cat.direction
    }

    const main = countdown.getMainCountdown(itemData, now)
    const elapsed = countdown.getElapsedText(itemData, now)

    const heartCopy = copyTemplates.getCopy(
      raw.categoryId,
      elapsed.isPast,
      elapsed.totalDays,
      elapsed.years
    )

    let detailMain = ''
    let detailSub = heartCopy

    if (elapsed.isPast && itemData.isRecurring) {
      detailMain = elapsed.text
    } else if (main.isPast) {
      detailMain = `已过 ${main.days} 天`
    } else {
      detailMain = `还有 ${main.days} 天`
    }

    const milestone = itemData.isRecurring
      ? null
      : countdown.getNextMilestone(raw.targetDate, main.isPast ? -main.days : main.days)

    this.setData({
      item: {
        ...raw,
        isPast: main.isPast,
        preciseIsPast: main.isPast,
        countdownPreciseDays: main.days,
        countdownPrecise: main.totalFormatted,
        countdownHms: (main.totalFormatted.split(' ')[1] || ''),
        countdownSentence: elapsed.text,
        detailMain,
        detailSub,
        dateStr: this.formatDate(raw.targetDate),
        icon: cat.icon,
        name: cat.name,
        milestone: milestone
          ? `距离${milestone.milestone}天纪念日还有 ${milestone.daysLeft} 天`
          : null,
        isRecurring: itemData.isRecurring
      },
      remindEnabled: raw.remindDays >= 0,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
  },

  formatDate(dateStr) {
    const d = new Date(dateStr)
    return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`
  },

  goBack() { wx.navigateBack() },

  goToEdit() {
    wx.navigateTo({ url: `/pages/add/add?id=${this.data.id}` })
  },

  toggleRemind() {
    const items = wx.getStorageSync('countdownItems') || []
    const index = items.findIndex(i => i.id === this.data.id)
    if (index > -1) {
      const current = items[index].remindDays
      items[index].remindDays = current >= 0 ? -1 : 1
      wx.setStorageSync('countdownItems', items)
      this.setData({ remindEnabled: items[index].remindDays >= 0 })
      wx.showToast({
        title: items[index].remindDays >= 0 ? '已开启提醒' : '已关闭提醒',
        icon: 'success'
      })
    }
  },

  shareCard() {
    const item = this.data.item
    if (!item) return
    wx.showLoading({ title: '生成中...' })
    const ctx = wx.createCanvasContext('shareCanvas')
    const st = getShareTheme(item.categoryId)
    const hasCover = !!(item.coverImage)

    if (hasCover) {
      // ── 有封面图：图片作背景 + 渐变叠加 + 文字 ──
      ctx.drawImage(item.coverImage, 0, 0, 300, 420)
      // 底部渐变暗遮罩
      ctx.setFillStyle('rgba(0,0,0,0.55)')
      ctx.fillRect(0, 180, 300, 240)
      // 顶部轻微遮罩
      ctx.setFillStyle('rgba(0,0,0,0.18)')
      ctx.fillRect(0, 0, 300, 60)
    } else {
      // ── 无封面：纯色/渐变背景 ──
      ctx.setFillStyle(st.bg)
      ctx.fillRect(0, 0, 300, 420)
    }

    // ── 文字层 ──
    ctx.setTextAlign('center')

    // 顶部标签
    ctx.setFontSize(13)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.9)' : st.accentColor)
    ctx.fillText(`${st.emoji}  ${item.name}`, 150, 38)

    // 分隔线
    ctx.setStrokeStyle(hasCover ? 'rgba(255,255,255,0.25)' : st.accentColor)
    ctx.setLineWidth(0.5)
    ctx.setGlobalAlpha(0.3)
    ctx.beginPath()
    ctx.moveTo(80, 52)
    ctx.lineTo(220, 52)
    ctx.stroke()
    ctx.setGlobalAlpha(1)

    // 主数字
    ctx.setFillStyle(hasCover ? '#FFFFFF' : st.numColor)
    ctx.font = '200 88px Georgia, serif'
    ctx.fillText(item.countdownPreciseDays.toString(), 150, 148)

    // 天标签
    ctx.setFontSize(18)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.75)' : st.labelColor)
    ctx.font = '300 18px sans-serif'
    ctx.fillText(item.preciseIsPast ? '天已过' : '天', 150, 172)

    // 时分秒
    ctx.setFontSize(20)
    ctx.setGlobalAlpha(0.5)
    const hms = (item.countdownPrecise.split(' ')[1] || '')
    ctx.fillText(hms, 150, 200)
    ctx.setGlobalAlpha(1)

    // 标题
    ctx.setFontSize(22)
    ctx.setFillStyle(hasCover ? '#FFFFFF' : st.titleColor)
    ctx.font = 'bold 22px sans-serif'
    ctx.fillText(item.title, 150, 248)

    // 日期
    ctx.setFontSize(14)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.7)' : st.subColor)
    ctx.font = '14px sans-serif'
    ctx.fillText(item.dateStr, 150, 276)

    // 温馨话
    ctx.setFontSize(13)
    ctx.setFillStyle(hasCover ? 'rgba(255,228,181,0.9)' : st.accentColor)
    ctx.setGlobalAlpha(0.88)
    ctx.fillText(item.detailSub, 150, 328)
    ctx.setGlobalAlpha(1)

    // 底部水印
    ctx.setFontSize(11)
    ctx.setFillStyle(hasCover ? 'rgba(255,255,255,0.4)' : st.subColor)
    ctx.setGlobalAlpha(0.4)
    ctx.fillText('No Forget · 值得记住的日子', 150, 408)
    ctx.setGlobalAlpha(1)

    ctx.draw(false, () => {
      wx.canvasToTempFilePath({
        canvasId: 'shareCanvas',
        x: 0, y: 0, width: 300, height: 420,
        destWidth: 600, destHeight: 840,
        fileType: 'png',
        success: (res) => {
          wx.hideLoading()
          wx.showShareImageMenu({
            itemList: ['分享给朋友', '分享到朋友圈'],
            imageUrl: res.tempFilePath
          })
        },
        fail: () => {
          wx.hideLoading()
          wx.showShareMenu({ withShareTicket: true })
        }
      })
    })
  }
})
