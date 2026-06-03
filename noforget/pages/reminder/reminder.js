// pages/reminder/reminder.js - 提醒设置页面逻辑

const countdownStore = require('../../utils/countdownStore.js')
const categories = require('../../utils/categories.js')
const periodCloud = require('../../utils/periodCloud.js')
const { SUBSCRIBE_TEMPLATES } = require('../../config/constant.js')
const { parseDateSafe: _parseDateSafe } = require('../../utils/date-utils.js')

// ─── 工具函数（兼容包装，保持返回 null/'—' 的原有行为）──
function parseDateSafe(value) {
  const d = _parseDateSafe(value)
  return isNaN(d.getTime()) ? null : d
}

function formatDate(date) {
  if (!date) return '—'
  const d = parseDateSafe(date)
  if (!d) return '—'
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getCategoryInfo(categoryId) {
  const cat = categories.getCategoryById(categoryId)
  return cat || { icon: '📌', name: '纪念日', color: '#9C8C82' }
}

function getRemindDaysText(days) {
  if (days === 0) return '当天'
  if (days === 1) return '提前1天'
  return `提前${days}天`
}

Page({
  data: {
    statusBarHeight: 20,
    isSubscribed: false,

    // 已开启提醒列表
    reminderItems: [],

    // 姨妈提醒
    periodRemindEnabled: false,
    periodAdvanceOptions: [
      { value: 0, label: '当天' },
      { value: 1, label: '1天前' },
      { value: 2, label: '2天前' },
      { value: 3, label: '3天前' },
      { value: 5, label: '5天前' },
      { value: 7, label: '7天前' }
    ],
    periodAdvanceIndex: 1
  },

  onLoad() {
    this.initNavigation()
  },

  initNavigation() {
    try {
      const windowInfo = wx.getWindowInfo()
      const menuButton = wx.getMenuButtonBoundingClientRect()
      const statusBarHeight = windowInfo.statusBarHeight || 20
      const navBarHeight = (menuButton.top - statusBarHeight) * 2 + menuButton.height
      this.setData({
        statusBarHeight,
        navBarHeight: Math.round(navBarHeight),
        totalTopHeight: Math.round(statusBarHeight + navBarHeight)
      })
    } catch(e) {
      this.setData({ statusBarHeight: 20, navBarHeight: 44, totalTopHeight: 64 })
    }
  },

  onShow() {
    this.checkSubscriptionStatus()
    this.loadReminderItems()
    this.loadPeriodSettings()
  },

  // ─── 检查微信订阅消息授权状态 ──────────
  checkSubscriptionStatus() {
    try {
      wx.getSetting({
        withSubscriptions: true,
        success: (res) => {
          // subscriptionsSetting.itemSettings 包含各模板ID的授权状态
          const subSetting = res.subscriptionsSetting || {}
          const itemSettings = subSetting.itemSettings || {}
          // 检查是否至少有一个模板被接受
          const hasAccepted = Object.values(itemSettings).some(v => v === 'accept')
          // 同时检查主开关
          const mainSwitch = subSetting.mainSwitch !== false

          this.setData({
            isSubscribed: hasAccepted && mainSwitch
          })
        },
        fail: () => {
          // 降级：检查storage中是否有订阅记录
          try {
            const subRecord = wx.getStorageSync('periodSubscribed')
            this.setData({ isSubscribed: !!subRecord })
          } catch (e) {
            this.setData({ isSubscribed: false })
          }
        }
      })
    } catch (e) {
      console.error('[reminder] checkSubscriptionStatus failed:', e)
      this.setData({ isSubscribed: false })
    }
  },

  // ─── 打开订阅授权 ──────────────────────
  // ⚠️ 微信限制单次最多3个模板ID，当前刚好3个
  openSubscribe() {
    const tmplIds = [
      SUBSCRIBE_TEMPLATES.PERIOD,
      SUBSCRIBE_TEMPLATES.DANGER,
      SUBSCRIBE_TEMPLATES.COUNTDOWN
    ].filter(Boolean)

    if (!tmplIds.length) {
      wx.showToast({ title: '提醒模板未配置', icon: 'none' })
      return
    }

    wx.requestSubscribeMessage({
      tmplIds,
      success: async (res) => {
        // 检查是否有模板被接受
        const hasAccepted = Object.values(res).some(v => v === 'accept')
        try {
          await periodCloud.syncSubscribed(hasAccepted)
        } catch (e) {
          console.error('[reminder] syncSubscribed failed:', e)
          wx.setStorageSync('periodSubscribed', hasAccepted)
        }
        if (hasAccepted) {
          wx.showToast({ title: '订阅成功', icon: 'success' })
          this.setData({ isSubscribed: true })
        } else {
          wx.showToast({ title: '已取消', icon: 'none' })
          this.setData({ isSubscribed: false })
        }
      },
      fail: (err) => {
        console.error('[reminder] requestSubscribeMessage failed:', err)
        wx.showToast({ title: '授权失败', icon: 'none' })
      }
    })
  },

  // ─── 加载已开启提醒的纪念日列表 ────────
  async loadReminderItems() {
    try {
      const items = await countdownStore.getItems()
      // 筛选 remindDays >= 0 的纪念日（排除姨妈项）
      const filtered = items.filter(item => {
        if (!item || !item.id) return false
        if (item.categoryId === 'period') return false
        const remindDays = item.remindDays
        return Number.isFinite(remindDays) && remindDays >= 0
      })

      const enriched = filtered.map(item => {
        const catInfo = getCategoryInfo(item.categoryId)
        return {
          ...item,
          icon: catInfo.icon,
          targetDateText: formatDate(item.targetDate),
          remindDaysText: getRemindDaysText(item.remindDays)
        }
      })

      this.setData({ reminderItems: enriched })
    } catch (e) {
      console.error('[reminder] loadReminderItems failed:', e)
      this.setData({ reminderItems: [] })
    }
  },

  // ─── 加载姨妈提醒设置 ──────────────────
  loadPeriodSettings() {
    try {
      const periodSettings = wx.getStorageSync('periodSettings') || {}
      const remindEnabled = periodSettings.remindEnabled !== false
      const remindBefore = Number.isFinite(periodSettings.remindBefore)
        ? periodSettings.remindBefore
        : 1

      let periodAdvanceIndex = 1
      const opts = this.data.periodAdvanceOptions
      for (let i = 0; i < opts.length; i++) {
        if (opts[i].value === remindBefore) {
          periodAdvanceIndex = i
          break
        }
      }

      this.setData({
        periodRemindEnabled: remindEnabled,
        periodAdvanceIndex
      })
    } catch (e) {
      console.error('[reminder] loadPeriodSettings failed:', e)
    }
  },

  // ─── 姨妈提醒开关 ──────────────────────
  onPeriodRemindChange(e) {
    const enabled = !!e.detail.value
    this.setData({ periodRemindEnabled: enabled })
    try {
      const periodSettings = wx.getStorageSync('periodSettings') || {}
      periodSettings.remindEnabled = enabled
      wx.setStorageSync('periodSettings', periodSettings)
    } catch (err) {
      console.error('[reminder] save periodSettings failed:', err)
    }
  },

  // ─── 姨妈提醒提前天数 ──────────────────
  onPeriodAdvanceChange(e) {
    const index = parseInt(e.detail.value, 10)
    const days = this.data.periodAdvanceOptions[index].value
    this.setData({ periodAdvanceIndex: index })
    try {
      const periodSettings = wx.getStorageSync('periodSettings') || {}
      periodSettings.remindBefore = days
      wx.setStorageSync('periodSettings', periodSettings)
    } catch (err) {
      console.error('[reminder] save periodSettings failed:', err)
    }
  },

  // ─── 跳转到纪念日详情页 ────────────────
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // ─── 返回上一页 ────────────────────────
  goBack() {
    const pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.reLaunch({ url: '/pages/mine/mine' })
    }
  }
})
