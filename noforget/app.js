// app.js - No Forget 入口文件
const themeModule = require('./utils/theme.js')
const countdownStore = require('./utils/countdownStore.js')
const { CLOUD_ENV_ID } = require('./config/constant.js')

// 让 app.js 和 utils/theme.js 共用同一份主题数据
// globalData.themes = color-value版本（供各页面 setData 绑定）
// utils/theme.js = cssVars版本（供 wxss 变量注入）

App({
  globalData: {
    userInfo: null,
    hasLogin: false,
    enableCloudSync: false,
    // themes 从 utils/theme.js 引入，保持两份数据同步
    themes: themeModule.themes,
    currentTheme: 'apple'
  },

  onLaunch() {
    // 微信隐私授权处理（2023.09.15起强制要求）
    if (typeof wx.onNeedPrivacyAuthorization === 'function') {
      wx.onNeedPrivacyAuthorization((resolve) => {
        wx.showModal({
          title: '隐私授权',
          content: 'NoForget 需要获取你的微信 OpenID 用于云端数据同步。你的所有数据仅存储在你自己可见的云空间，未经授权不会分享给第三方。',
          confirmText: '同意',
          cancelText: '拒绝',
          success: (res) => {
            if (res.confirm) {
              resolve({ event: 'agree', buttonId: 'agree' })
            } else {
              resolve({ event: 'disagree' })
            }
          },
          fail: () => {
            resolve({ event: 'disagree' })
          }
        })
      })
    }

    // 初始化云开发
    if (!wx.cloud) {
      // 当前微信版本不支持云开发，静默降级
    } else {
      try {
        wx.cloud.init({
          env: CLOUD_ENV_ID,
          traceUser: true
        })
        // 启动后异步同步，不阻塞用户首帧
        setTimeout(() => {
          countdownStore.bootstrapSync().catch((e) => { console.error('[app] bootstrapSync failed:', e) })
        }, 0)
      } catch (error) {
        console.error('[app] cloud init failed:', error)
        // 云开发初始化失败，静默降级本地模式
      }
    }

    // 检查登录状态（启动时同步读取，不阻塞）
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.globalData.userInfo = userInfo
      this.globalData.hasLogin = true
    }
  },

  // 静默登录：通过云函数获取 openid（免用户授权）
  // 头像/昵称改为用户主动填写（见 mine 页面 chooseAvatar + type nickname）
  // wx.getUserProfile 已废弃（2023.04起返回匿名信息），不再使用
  async doLogin(callback) {
    try {
      if (!wx.cloud) {
        if (callback) callback(null)
        return
      }
      const res = await wx.cloud.callFunction({
        name: 'countdown-sync',
        data: { action: 'whoami' }
      })
      const openid = res.result?.openid || null
      this.globalData.hasLogin = !!openid
      if (callback) callback(openid)
    } catch (e) {
      console.error('doLogin failed:', e)
      if (callback) callback(null)
    }
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
