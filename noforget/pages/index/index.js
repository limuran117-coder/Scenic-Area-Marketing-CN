// pages/index/index.js - 首页逻辑
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')

Page({
  data: {
    statusBarHeight: 20,
    items: [],
    hasLogin: false,
    userInfo: null,
    showThemePicker: false,
    currentTheme: 'apple',
    theme: {},
    hasMore: false,
    page: 1,
    pageSize: 10
  },

  onLoad() {
    // 获取状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight
    })
  },

  onShow() {
    // 检查登录状态
    const userInfo = app.globalData.userInfo
    const hasLogin = app.globalData.hasLogin
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    
    this.setData({
      userInfo,
      hasLogin,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
    
    // 加载数据
    this.loadItems()
  },

  // 加载倒计时列表
  loadItems() {
    // 先从本地存储读取
    const localData = wx.getStorageSync('countdownItems') || []
    
    // 计算每个倒计时的最新数据
    const now = new Date()
    const processedItems = localData.map(item => {
      const diff = countdown.getExactDiff(new Date(item.targetDate), now)
      const cat = categories.getCategoryById(item.categoryId)
      const d = new Date(item.targetDate)
      const dateStr = `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`


      return {
        ...item,
        days: diff.totalDays,
        isPast: diff.isPast,
        detailText: countdown.formatDisplayText(diff, item.direction === 'countup'),
        icon: cat.icon,
        name: cat.name,
        dateStr: dateStr
      }
    })
    
    // 按日期排序（即将到来的排前面）
    processedItems.sort((a, b) => {
      // 如果一个已过一个未过，未过的排前面
      if (a.isPast !== b.isPast) {
        return a.isPast ? 1 : -1
      }
      // 都是未过的，按天数升序
      if (!a.isPast) {
        return a.days - b.days
      }
      // 都是已过的，按天数降序（已过越久的排前面）
      return b.days - a.days
    })
    
    this.setData({
      items: processedItems,
      hasMore: processedItems.length >= this.data.pageSize
    })
  },

  // 去登录
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

  // 打开主题选择器
  openThemePicker() {
    this.setData({
      showThemePicker: true
    })
  },

  // 关闭主题选择器
  closeThemePicker() {
    this.setData({
      showThemePicker: false
    })
  },

  // 阻止事件冒泡
  stopProp(e) {
    // 空实现，仅为catchtap
  },

  // 选择主题
  selectTheme(e) {
    const themeId = e.currentTarget.dataset.theme
    app.setTheme(themeId)
    this.setData({
      currentTheme: themeId,
      theme: app.globalData.themes[themeId],
      showThemePicker: false
    })
  },

  // 跳转到添加页面
  goToAdd() {
    wx.navigateTo({
      url: '/pages/add/add'
    })
  },

  // 跳转到详情页
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 跳转到我的页面
  goToMine() {
    wx.navigateTo({
      url: '/pages/mine/mine'
    })
  },

  // 分享卡片
  shareCard(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.items.find(i => i.id === id)
    if (!item) return

    // 生成分享海报
    wx.showLoading({
      title: '生成中...'
    })

    // 使用 canvas 生成分享图片
    const ctx = wx.createCanvasContext('shareCanvas')

    // 设置样式
    const theme = this.data.theme
    ctx.setFillStyle(theme.background)
    ctx.fillRect(0, 0, 300, 400)

    ctx.setFillStyle(theme.textPrimary)
    ctx.setFontSize(28)
    ctx.fillText(item.days.toString(), 150, 150)
    ctx.setFontSize(14)
    ctx.setFillStyle(theme.textSecondary)
    ctx.fillText(item.isPast ? '天已过' : '天', 150, 180)
    ctx.setFontSize(16)
    ctx.fillText(item.title, 150, 220)
    ctx.setFontSize(12)
    ctx.fillText(item.dateStr, 150, 250)
    ctx.fillText('No Forget', 150, 380)

    ctx.draw()

    setTimeout(() => {
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
          wx.showToast({
            title: '生成失败',
            icon: 'none'
          })
        }
      })
    }, 500)
  },

  // 加载更多
  loadMore() {
    if (!this.data.hasMore) return
    this.setData({
      page: this.data.page + 1
    })
    this.loadItems()
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadItems()
    wx.stopPullDownRefresh()
  }
})
