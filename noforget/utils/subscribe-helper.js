const {SUBSCRIBE_TEMPLATES, SUBSCRIBE_CONFIG} = require('../config/constant.js')
const periodCloud = require('./periodCloud.js')

// 姨妈订阅消息助手
const SubscribeHelper = {
  // 检查是否需要请求授权（拒绝后3天内不弹）
  needRequest() {
    try {
      const lastReject = wx.getStorageSync('lastReject_period') || 0
      // 检查用户是否已在系统设置中永久关闭了订阅
      try {
        const setting = wx.getSettingSync ? wx.getSettingSync() : null
        if (setting && setting.subscriptionsSetting && setting.subscriptionsSetting.mainSwitch === false) {
          return false
        }
      } catch (e) { console.error('[subscribe] getSetting failed:', e) }
      return Date.now() - lastReject > SUBSCRIBE_CONFIG.retryInterval
    } catch (e) {
      console.error('[subscribe] needRequest failed:', e)
      return false
    }
  },

  // 请求用户授权（核心接口）
  requestAuth() {
    return new Promise((resolve) => {
      // 先弹引导框，让用户知道为什么需要授权
      wx.showModal({
        title: '开启姨妈提醒',
        content: SUBSCRIBE_CONFIG.authTips,
        confirmText: '立即开启',
        cancelText: '暂不需要',
        success: async (res) => {
          if (!res.confirm) {
            // 用户拒绝 → 记录时间戳，3天内不再弹
            try {
              wx.setStorageSync('lastReject_period', Date.now())
            } catch (e) {}
            return resolve(false)
          }

          // 用户确认 → 调用微信官方订阅接口（同时请求3个模板）
          // ⚠️ 微信限制单次最多3个模板ID，当前刚好3个
          try {
            const tmplIds = [
              SUBSCRIBE_TEMPLATES.PERIOD,
              SUBSCRIBE_TEMPLATES.DANGER,
              SUBSCRIBE_TEMPLATES.COUNTDOWN
            ].filter(Boolean)
            if (!tmplIds.length) {
              wx.showToast({title: '提醒模板未配置', icon: 'none'})
              return resolve(false)
            }
            wx.requestSubscribeMessage({
              tmplIds,
              success: async (res) => {
                const acceptPeriod = res[SUBSCRIBE_TEMPLATES.PERIOD] === 'accept'
                const acceptDanger = res[SUBSCRIBE_TEMPLATES.DANGER] === 'accept'
                const acceptCountdown = res[SUBSCRIBE_TEMPLATES.COUNTDOWN] === 'accept'

                if (acceptPeriod || acceptDanger || acceptCountdown) {
                  // ★ 修复：await 确保云同步完成，失败时有日志
                  try {
                    await periodCloud.syncSubscribed(true)
                  } catch (e) {
                    console.error('[subscribe] syncSubscribed failed:', e)
                  }
                  wx.showToast({title: '订阅成功！', icon: 'success'})
                } else {
                  try {
                    await periodCloud.syncSubscribed(false)
                  } catch (e) {
                    console.error('[subscribe] syncSubscribed failed:', e)
                  }
                  wx.showToast({title: '已取消订阅', icon: 'none'})
                }
                resolve(true)
              },
              fail: (err) => {
                console.error('订阅消息授权失败', err)
                wx.showToast({title: '授权失败', icon: 'none'})
                resolve(false)
              }
            })
          } catch (e) {
            wx.showToast({title: '订阅接口异常', icon: 'none'})
            resolve(false)
          }
        }
      })
    })
  },

  // 发送订阅消息（云函数触发，暂未实现）
  async sendReminder() {
    console.log('sendReminder 待接入云函数')
  }
}

module.exports = SubscribeHelper
