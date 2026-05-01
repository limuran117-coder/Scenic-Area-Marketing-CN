// app.js - No Forget 入口文件
const app = getApp()
const themeModule = require('./utils/theme.js')

// 让 app.js 和 utils/theme.js 共用同一份主题数据
// globalData.themes = color-value版本（供各页面 setData 绑定）
// utils/theme.js = cssVars版本（供 wxss 变量注入）

App({
  globalData: {
    userInfo: null,
    hasLogin: false,
    // themes 从 utils/theme.js 引入，保持两份数据同步
    themes: themeModule.themes,
    currentTheme: 'apple'
  },

  onLaunch() {
    // 初始化云开发
    if (!wx.cloud) {
      console.warn('当前微信版本不支持云开发')
    } else {
      wx.cloud.init({
        env: 'noforget-cloud-xxxxx', // 云环境ID，后续配置
        traceUser: true,
      })
    }

    // 检查登录状态
    this.checkLoginStatus()
  },

  // 检查登录状态
  checkLoginStatus() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.globalData.userInfo = userInfo
      this.globalData.hasLogin = true
    }
  },

  // 微信登录
  doLogin(callback) {
    wx.getUserProfile({
      desc: '用于展示你的倒计时卡片',
      success: (res) => {
        const userInfo = {
          nickName: res.userInfo.nickName,
          avatarUrl: res.userInfo.avatarUrl,
          gender: res.userInfo.gender,
          country: res.userInfo.country,
          province: res.userInfo.province,
          city: res.userInfo.city
        }
        this.globalData.userInfo = userInfo
        this.globalData.hasLogin = true
        wx.setStorageSync('userInfo', userInfo)
        callback && callback(userInfo)
      },
      fail: (err) => {
        console.error('登录失败', err)
        wx.showToast({
          title: '请允许授权',
          icon: 'none'
        })
      }
    })
  },

  // 获取当前主题对象
  getTheme() {
    return this.globalData.themes[this.globalData.currentTheme]
  },

  // 获取当前强调色（便捷访问）
  getAccentColor() {
    return this.globalData.themes[this.globalData.currentTheme]?.textAccent || '#0066cc'
  },


  // 切换主题
  setTheme(themeId) {
    if (this.globalData.themes[themeId]) {
      this.globalData.currentTheme = themeId
      wx.setStorageSync('currentTheme', themeId)
    }
  }
})
