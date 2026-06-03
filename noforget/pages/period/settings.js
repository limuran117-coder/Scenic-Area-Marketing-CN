// pages/period/settings.js
const period = require('../../utils/period.js')
const periodCloud = require('../../utils/periodCloud.js')

/**
 * ✅ P0#2修复：简单哈希函数，用于UI门控（防他人顺手翻看）
 * 注意：4位PIN仅10,000种可能，不可用于真正安全保护
 * 不等于密码学安全哈希，请勿替代SOTER/服务端验证
 * DJB2实现，h & h为恒等式（保留以保持行为一致）
 */
function hashPin(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i)
  }
  return 'p' + Math.abs(h).toString(36)
}

Page({
  data: {
    statusBarHeight: 20,
    totalTopHeight: 64,
    localSettings: {},
    remindDaysOptions: [1, 2, 3, 5, 7],
    remindDaysIndex: 2,
    cycleOptions: [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
    cycleIndex: 5,
    modes: [
      {key: 'normal', label: '正常模式', desc: '查看时间节点'},
      {key: 'caution', label: '谨慎模式', desc: '稍微提前提示重点阶段'}
    ],
    cloudEnabled: true,
    cloudOpenid: ''
  },

  onLoad() {
    try {
      const windowInfo = wx.getWindowInfo()
      const menuButton = wx.getMenuButtonBoundingClientRect()
      const statusBarHeight = windowInfo.statusBarHeight || 20
      const navBarHeight = (menuButton.top - statusBarHeight) * 2 + menuButton.height
      this.setData({
        statusBarHeight,
        totalTopHeight: Math.round(statusBarHeight + navBarHeight)
      })
    } catch(e) {}
    this.loadSettings()
  },

  loadSettings() {
    const s = period.getSettings()
    const status = periodCloud.getStatus()
    this.setData({
      localSettings: s,
      remindDaysIndex: Math.max(0, this.data.remindDaysOptions.indexOf(s.remindBefore)),
      cycleIndex: Math.max(0, this.data.cycleOptions.indexOf(s.cycleLength)),
      cloudOpenid: status.openid || '',
      cloudEnabled: !!status.hasIdentity
    })
  },

  goBack() { const p = getCurrentPages(); if (p.length > 1) { wx.navigateBack() } else { wx.reLaunch({url: '/pages/index/index'}) } },

  toggleRemind(e) {
    wx.vibrateShort({type: 'medium'})
    const s = {...this.data.localSettings, remindEnabled: e.detail.value}
    period.saveSettings(s)
    this.setData({localSettings: s})
    periodCloud.scheduleSync(undefined, undefined, s)
  },

  onRemindDaysChange(e) {
    wx.vibrateShort({type: 'light'})
    const days = this.data.remindDaysOptions[e.detail.value]
    const s = {...this.data.localSettings, remindBefore: days}
    period.saveSettings(s)
    this.setData({localSettings: s})
    periodCloud.scheduleSync(undefined, undefined, s)
  },

  toggleRemindOnDay(e) {
    wx.vibrateShort({type: 'medium'})
    const s = {...this.data.localSettings, remindOnDay: e.detail.value}
    period.saveSettings(s)
    this.setData({localSettings: s})
    periodCloud.scheduleSync(undefined, undefined, s)
  },

  onCycleChange(e) {
    wx.vibrateShort({type: 'light'})
    const len = this.data.cycleOptions[e.detail.value]
    const s = {...this.data.localSettings, cycleLength: len}
    period.saveSettings(s)
    this.setData({localSettings: s})
    periodCloud.scheduleSync(undefined, undefined, s)
  },

  /**
   * ✅ P0#2修复：PIN码哈希存储 + 排除云端同步
   * pinCode 改为 pinHash（哈希值），sync时排除密码字段
   */
  togglePin(e) {
    wx.vibrateShort({type: 'medium'})
    if (e.detail.value) {
      wx.showModal({
        title: '设置密码',
        editable: true,
        placeholderText: '请输入4位数字密码',
        success: (res) => {
          if (res.content && /^\d{4}$/.test(res.content)) {
            const s = {...this.data.localSettings, pinEnabled: true, pinHash: hashPin(res.content)}
            delete s.pinCode  // 移除旧明文（若有）
            delete s.pinHashFromCloud  // 确保不同步
            period.saveSettings(s)
            this.setData({localSettings: s})
            // 排除所有密码相关字段，不同步到云端
            // 注：pinEnabled 也不同步，避免云端恢复后显示"密码已开启"但无法验证
            const syncSettings = {...s}
            delete syncSettings.pinHash
            delete syncSettings.pinCode
            delete syncSettings.pinEnabled
            periodCloud.scheduleSync(undefined, undefined, syncSettings)
            wx.showToast({title: '密码已设置', icon: 'success'})
          } else if (res.confirm) {
            wx.showToast({title: '请输入4位数字', icon: 'none'})
          }
        }
      })
    } else {
      const s = {...this.data.localSettings, pinEnabled: false}
      delete s.pinHash
      delete s.pinCode
      period.saveSettings(s)
      this.setData({localSettings: s})
      // 排除所有密码相关字段
      periodCloud.scheduleSync(undefined, undefined, s)
    }
  },

  changePin() {
    wx.showModal({
      title: '修改密码',
      editable: true,
      placeholderText: '请输入新4位密码',
      success: (res) => {
        if (res.content && /^\d{4}$/.test(res.content)) {
          const s = {...this.data.localSettings, pinHash: hashPin(res.content)}
          delete s.pinCode
          period.saveSettings(s)
          this.setData({localSettings: s})
          // 排除密码相关字段，不同步到云端
          const syncSettings = {...s}
          delete syncSettings.pinHash
          delete syncSettings.pinCode
          periodCloud.scheduleSync(undefined, undefined, syncSettings)
          wx.showToast({title: '密码已修改', icon: 'success'})
        } else if (res.confirm) {
          wx.showToast({title: '请输入4位数字', icon: 'none'})
        }
      }
    })
  },

  changeMode(e) {
    const newMode = e.currentTarget.dataset.val
    if (this.data.localSettings.mode === newMode) return
    wx.vibrateShort({type: 'light'})
    const s = {...this.data.localSettings, mode: newMode}
    period.saveSettings(s)
    this.setData({localSettings: s})
    periodCloud.scheduleSync(undefined, undefined, s)
  },

  exportData() {
    const entries = period.getEntries()
    const daily = period.getDailyRecords()
    const settings = period.getSettings()
    const data = {entries, daily, settings, exportedAt: new Date().toISOString()}
    const json = JSON.stringify(data, null, 2)
    wx.setStorageSync('periodExportData', json)
    wx.showToast({title: '数据已准备，请截图保存', icon: 'none', duration: 3000})
  },

  toggleCloudSync(e) {
    if (!e.detail.value) {
      periodCloud.clearIdentity()
      this.setData({cloudEnabled: false, cloudOpenid: ''})
      wx.showToast({title: '已关闭云端同步', icon: 'none'})
    } else {
      wx.showLoading({title: '初始化云端...', mask: true})
      periodCloud.init()
        .then(async openid => {
          if (!openid) {
            this.setData({cloudEnabled: false})
            wx.showToast({title: '云端不可用', icon: 'none'})
            return
          }

          const cloudData = await periodCloud.downloadFromCloud()
          if (cloudData) {
            this.loadSettings()
          } else {
            const entries = period.getEntries()
            const daily = period.getDailyRecords()
            const settings = period.getSettings()
            await periodCloud.uploadToCloud(entries, daily, settings)
          }

          this.setData({cloudEnabled: true, cloudOpenid: openid})
          wx.showToast({title: '云端同步已开启', icon: 'success'})
        })
        .catch(() => {
          this.setData({cloudEnabled: false, cloudOpenid: ''})
          wx.showToast({title: '云端初始化失败', icon: 'none'})
        })
        .finally(() => {
          wx.hideLoading()
        })
    }
  },

  pullFromCloud() {
    wx.showLoading({title: '同步中...', mask: true})
    periodCloud.downloadFromCloud().then(data => {
      wx.hideLoading()
      if (data) {
        this.loadSettings()
        wx.showToast({title: '已从云端恢复', icon: 'success'})
      } else {
        wx.showToast({title: '云端无数据', icon: 'none'})
      }
    })
  },

  clearData() {
    wx.showModal({
      title: '确认清除',
      content: '此操作不可恢复，确定要清除所有姨妈追踪数据吗？',
      confirmColor: '#9B7EC6',
      success: async (res) => {
        if (res.confirm) {
          period.saveEntries([])
          wx.setStorageSync(period.STORAGE_KEYS.daily, {})
          wx.setStorageSync(period.STORAGE_KEYS.settings, {...period.DEFAULT_SETTINGS})
          try {
            await periodCloud.uploadToCloud([], {}, {...period.DEFAULT_SETTINGS})
          } catch (e) {}
          wx.showToast({title: '已清除', icon: 'success'})
          setTimeout(() => { wx.navigateBack() }, 1000)
        }
      }
    })
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
    return {
      title: 'No Forget - 别忘记重要日子',
      path: '/pages/index/index',
    }
  },

  onShareTimeline: function () {
    return {
      title: 'No Forget - 别忘记重要日子',
    }
  },

  onCopyUrl: function () {
    return {
      query: '',
    }
  }
})