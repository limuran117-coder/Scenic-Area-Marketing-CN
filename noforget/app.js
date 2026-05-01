// app.js - No Forget 入口文件
const app = getApp()

App({
  globalData: {
    userInfo: null,
    hasLogin: false,
    // 四套主题配置
    // 基于 VoltAgent awesome-design-md × Impeccable 设计规范
    themes: {
      // Apple 主题 — 极简摄影感，白色留白，精准蓝强调
      apple: {
        id: 'apple',
        name: 'Apple',
        background: '#ffffff',
        cardBg: '#ffffff',
        textPrimary: '#1d1d1f',
        textSecondary: '#6e6e73',
        textAccent: '#0066cc',
        border: 'rgba(0,0,0,0.08)',
        shadow: '0 2px 12px rgba(0,0,0,0.07)',
      },
      // Notion 主题 — 暖白纸质感，超薄边框，柔和蓝强调
      notion: {
        id: 'notion',
        name: 'Notion',
        background: '#faf9f7',
        cardBg: '#ffffff',
        textPrimary: 'rgba(0,0,0,0.88)',
        textSecondary: '#9c9489',
        textAccent: '#2385e2',
        border: 'rgba(0,0,0,0.07)',
        shadow: '0 0 0 1px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)',
      },
      // Airbnb 主题 — 温暖珊瑚红，友好圆润，仪式感强
      airbnb: {
        id: 'airbnb',
        name: 'Airbnb',
        background: '#fafafa',
        cardBg: '#ffffff',
        textPrimary: '#1a1a1a',
        textSecondary: '#717171',
        textAccent: '#ff385c',
        border: '#f0f0f0',
        shadow: '0 4px 24px rgba(255,56,92,0.12)',
      },
      // Starbucks 主题 — 咖啡深绿，奶油白底，厚重温暖
      starbucks: {
        id: 'starbucks',
        name: 'Starbucks',
        background: '#f7f5f0',
        cardBg: '#ffffff',
        textPrimary: '#2d2018',
        textSecondary: '#7a7067',
        textAccent: '#1E3932',
        border: '#e8e2da',
        shadow: '0 4px 20px rgba(45,32,24,0.10)',
      }
    },
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

  // 获取当前主题
  getTheme() {
    return this.globalData.themes[this.globalData.currentTheme]
  },

  // 切换主题
  setTheme(themeId) {
    if (this.globalData.themes[themeId]) {
      this.globalData.currentTheme = themeId
      wx.setStorageSync('currentTheme', themeId)
    }
  }
})
