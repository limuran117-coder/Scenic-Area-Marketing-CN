// app.js - No Forget 入口文件
const app = getApp()

App({
  globalData: {
    userInfo: null,
    hasLogin: false,
    // 三套主题配置
    themes: {
      // Apple 风格 - 极简纯净
      apple: {
        id: 'apple',
        name: 'Apple 风格',
        background: '#FFFFFF',
        backgroundGrad: '',
        cardBg: '#F5F5F7',
        textPrimary: '#1D1D1F',
        textSecondary: '#86868B',
        textAccent: '#0071E3',
        border: '#E5E5E5',
        shadow: '0 2px 12px rgba(0,0,0,0.06)',
        emoji: ''
      },
      // 莫兰迪风格 - 低饱和高级灰
      morandi: {
        id: 'morandi',
        name: '莫兰迪风格',
        background: '#F2EDE8',
        backgroundGrad: '',
        cardBg: '#E8E2DC',
        textPrimary: '#5D5448',
        textSecondary: '#9C9486',
        textAccent: '#A78B7A',
        border: '#D4CEC6',
        shadow: '0 2px 12px rgba(93,84,72,0.1)',
        emoji: ''
      },
      // 复古风格 - 米黄棕色调
      vintage: {
        id: 'vintage',
        name: '复古风格',
        background: '#FBF7F0',
        backgroundGrad: '',
        cardBg: '#F5EFE6',
        textPrimary: '#4A3728',
        textSecondary: '#8B7355',
        textAccent: '#C4A35A',
        border: '#E0D5C5',
        shadow: '0 2px 12px rgba(74,55,40,0.1)',
        emoji: ''
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
