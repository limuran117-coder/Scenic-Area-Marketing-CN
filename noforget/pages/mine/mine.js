// pages/mine/mine.js - 我的页面逻辑
const app = getApp()
const countdown = require('../../utils/countdown.js')

Page({
  data: {
    statusBarHeight: 20,
    hasLogin: false,
    userInfo: null,
    theme: {},
    currentTheme: 'apple',
    stats: {
      total: 0,
      upcoming: 0,
      past: 0
    }
  },

  onLoad() {
    const systemInfo = wx.getSystemInfoSync()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    const hasLogin = app.globalData.hasLogin
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'

    this.setData({
      userInfo,
      hasLogin,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })

    this.loadStats()
  },

  loadStats() {
    const items = wx.getStorageSync('countdownItems') || []
    const now = new Date()

    let upcoming = 0
    let past = 0

    items.forEach(item => {
      const diff = countdown.getDiff(new Date(item.targetDate), now)
      if (diff.isPast) {
        past++
      } else {
        upcoming++
      }
    })

    this.setData({
      stats: {
        total: items.length,
        upcoming,
        past
      }
    })
  },

  doLogin() {
    app.doLogin((userInfo) => {
      this.setData({
        userInfo,
        hasLogin: true
      })
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      })
    })
  },

  exportData() {
    const items = wx.getStorageSync('countdownItems') || []
    if (items.length === 0) {
      wx.showToast({
        title: '暂无数据',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '导出中...'
    })

    // 转换为JSON并复制到剪贴板
    const jsonStr = JSON.stringify(items, null, 2)
    wx.setClipboardData({
      data: jsonStr,
      success: () => {
        wx.hideLoading()
        wx.showToast({
          title: '已复制到剪贴板',
          icon: 'success'
        })
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '导出失败',
          icon: 'none'
        })
      }
    })
  },

  contactUs() {
    wx.showModal({
      title: '意见反馈',
      content: '如果你有任何建议或问题，欢迎通过以下方式联系我们：',
      confirmText: '复制微信号',
      cancelText: '关闭',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: 'noforget2024',
            success: () => {
              wx.showToast({
                title: '已复制',
                icon: 'success'
              })
            }
          })
        }
      }
    })
  },

  goBack() {
    wx.navigateBack()
  }
})
