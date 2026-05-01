// pages/detail/detail.js - 详情页逻辑
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const copyTemplates = require('../../utils/copyTemplates.js')

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
      statusBarHeight: systemInfo.statusBarHeight,
      currentTheme,
      theme: app.globalData.themes[currentTheme],
      id: options.id
    })
  },

  onShow() {
    // 每次显示都重新计算+随机文案（因为时间在变化）
    this.loadItem()
  },

  loadItem() {
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    const items = wx.getStorageSync('countdownItems') || []
    const item = items.find(i => i.id === this.data.id)

    if (!item) {
      wx.showToast({
        title: '未找到',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1000)
      return
    }

    const now = new Date()
    const diff = countdown.getExactDiff(new Date(item.targetDate), now)
    const cat = categories.getCategoryById(item.categoryId)
    const milestone = countdown.getNextMilestone(new Date(item.targetDate), diff.totalDays)

    // 判断是显示已过还是未过
    const isPast = item.direction === 'countup' ? true : diff.isPast
    const displayDays = isPast ? diff.totalDays : diff.totalDays

    // 获取随机走心文案
    const heartCopy = copyTemplates.getCopy(item.categoryId, isPast, diff.totalDays, diff.years)

    // 详细描述
    let detailMain = ''
    let detailSub = ''

    if (isPast) {
      detailMain = `已经过去了 ${countdown.formatDisplayText(diff, true)}`
      if (diff.years >= 1) {
        detailSub = heartCopy
      } else if (diff.months >= 1) {
        detailSub = heartCopy
      } else {
        detailSub = heartCopy
      }
    } else {
      detailMain = countdown.formatDisplayText(diff, false)
      detailSub = heartCopy
      if (milestone) {
        detailSub += ` · ${milestone.milestone}天纪念日还有${milestone.daysLeft}天`
      }
    }

    this.setData({
      item: {
        ...item,
        displayDays,
        isPast,
        detailMain,
        detailSub,
        detailText: countdown.formatDisplayText(diff, item.direction === 'countup'),
        milestone: milestone ? `距离${milestone.milestone}天纪念日还有 ${milestone.daysLeft} 天` : null,
        dateStr: this.formatDate(item.targetDate),
        icon: cat.icon,
        name: cat.name
      },
      remindEnabled: item.remindDays >= 0,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
  },

  formatDate(dateStr) {
    const d = new Date(dateStr)
    const year = d.getFullYear()
    const month = d.getMonth() + 1
    const day = d.getDate()
    // 有封面时用点分隔便于阅读，无封面时用中文年月日
    return `${year}.${month}.${day}`
  },

  goBack() {
    wx.navigateBack()
  },

  goToEdit() {
    wx.navigateTo({
      url: `/pages/add/add?id=${this.data.id}`
    })
  },

  toggleRemind() {
    const items = wx.getStorageSync('countdownItems') || []
    const index = items.findIndex(i => i.id === this.data.id)
    if (index > -1) {
      const current = items[index].remindDays
      items[index].remindDays = current >= 0 ? -1 : 1
      wx.setStorageSync('countdownItems', items)
      this.setData({
        remindEnabled: items[index].remindDays >= 0
      })
      wx.showToast({
        title: items[index].remindDays >= 0 ? '已开启提醒' : '已关闭提醒',
        icon: 'success'
      })
    }
  },

  shareCard() {
    const item = this.data.item
    if (!item) return

    wx.showLoading({
      title: '生成中...'
    })

    wx.canvasToTempFilePath({
      canvasId: 'shareCanvas',
      success: (res) => {
        wx.hideLoading()
        wx.showShareImageMenu({
          itemList: ['分享给朋友', '分享到朋友圈'],
          imageUrl: res.tempFilePath
        })
      },
      fail: () => {
        wx.hideLoading()
        // 降级处理：使用系统分享
        wx.showShareMenu({
          withShareTicket: true
        })
      }
    })
  }
})
