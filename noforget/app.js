// app.js - No Forget 入口文件
const app = getApp()

App({
  globalData: {
    userInfo: null,
    hasLogin: false,
    // 四套主题配置（基于 VoltAgent awesome-design-md）
    themes: {
      // Apple 风格 - 极简纯净，摄影感
      apple: {
        id: 'apple',
        name: 'Apple',
        background: '#FFFFFF',
        cardBg: '#f5f5f7',
        textPrimary: '#1d1d1f',
        textSecondary: '#7a7a7a',
        textAccent: '#0066cc',
        border: '#e0e0e0',
        shadow: '0 2px 12px rgba(0,0,0,0.06)',
      },
      // Notion 风格 - 温暖纸质感，文艺中性
      notion: {
        id: 'notion',
        name: 'Notion',
        background: '#ffffff',
        cardBg: '#f6f5f4',
        textPrimary: 'rgba(0,0,0,0.95)',
        textSecondary: '#a39e98',
        textAccent: '#0075de',
        border: 'rgba(0,0,0,0.1)',
        shadow: '0 1px 3px rgba(0,0,0,0.04),0 1px 2px rgba(0,0,0,0.03)',
      },
      // Airbnb 风格 - 温暖珊瑚红，消费友好
      airbnb: {
        id: 'airbnb',
        name: 'Airbnb',
        background: '#ffffff',
        cardBg: '#f7f7f7',
        textPrimary: '#222222',
        textSecondary: '#6a6a6a',
        textAccent: '#ff385c',
        border: '#ebebeb',
        shadow: '0 4px 16px rgba(0,0,0,0.12)',
      },
      // Starbucks 风格 - 咖啡馆温暖感
      starbucks: {
        id: 'starbucks',
        name: 'Starbucks',
        background: '#f2f0eb',
        cardBg: '#edebe9',
        textPrimary: 'rgba(0,0,0,0.87)',
        textSecondary: 'rgba(0,0,0,0.58)',
        textAccent: '#00754a',
        border: '#ddddd',
        shadow: '0 4px 12px rgba(0,0,0,0.14)',
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
