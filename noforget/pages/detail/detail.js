// pages/detail/detail.js - 详情页逻辑 v5
// 修复：导航栏高度用官方公式（statusBarHeight + navBarHeight）

const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const copyTemplates = require('../../utils/copyTemplates.js')
const countdownStore = require('../../utils/countdownStore.js')
const { parseDateSafe } = require('../../utils/date-utils.js')

// 🌟 情绪文案引擎（与首页共享）
function getEmotionalStatus(categoryId, isPast, itemId = '0') {
  const generalFuture = ['向着美好奔赴','满怀欣喜的倒数','时光酝酿的惊喜','距离美好的日子','静候佳音的那天','一切都在变好','准备迎接新篇章','美好正在路上','心怀期许的倒数','期待那一刻的到来']
  const generalPast = ['岁月留痕的第','时光沉淀的第','这美好已发生','历久弥新的第','值得铭记的第','熠熠生辉的第','悄悄溜走的第','温柔相伴的第','如影随形的第','岁月静好的第']
  const dict = {
    birthday: {future: ['距离下一次长大','期待新的一岁','距离专属纪念日','愿这一岁更闪耀','生辰倒数记','奔赴下一个生日'], past: ['已降临这世界','岁月的温柔馈赠','成长轨迹的第','生命绽放的第','来到地球的第','无畏成长的第']},
    pet_birthday: {future: ['距离拆罐头的日子','期待毛孩子的狂欢','准备专属奖励','接它回家的纪念'], past: ['毛孩子已陪伴','治愈时光的第','相伴打闹的第','温暖陪伴的第','摇尾巴的第']},
    love: {future: ['期待专属的怦然心动','距离浪漫时刻','爱意蔓延的倒数','距离见面的那天'], past: ['相爱相守的第','心动延续的第','携手走过的第','浪漫相伴的第','偏爱永存的第']},
    wedding: {future: ['期待婚礼纪念日','重温誓言的那一天','距离白纱与西装','期待浪漫重演'], past: ['幸福携手的第','执子之手的第','承诺兑现的第','爱意交织的第','白首之约的第']},
    death: {future: ['距离下一次缅怀','思念遥寄的日子','带着花去看你','静静怀念的那天'], past: ['思念蔓延的第','仰望星空的第','永留心间的第','默默祈福的第','化作漫天星辰']},
    festival: {future: ['期待佳节的到来','距离下一次欢聚','期待烟火与相聚','节日倒计时的喜悦'], past: ['这欢聚已过去','节日记忆的第','美好留存的第','时光沉淀的第','烟火散去的第']},
    repayment: {future: ['搞钱要紧，按时还款','距离账单日还有','守信是最大的财富','马上清空账单'], past: ['账单已出','记得到期还款哦','逾期可是不好的','信用积累的第']},
    period: {future: ['多喝热水照顾自己','距离特殊日子还有','提前备好红糖水','记得不要贪凉'], past: ['特殊时期的第','好好爱自己的第','辛苦的日子已过','贴心陪伴的第']},
    onboarding: {future: ['期待职场新篇章','下个职业里程碑','打怪升级倒计时','准备迎接新挑战'], past: ['职场深耕的第','默默拔尖的第','发光发热的第','努力搬砖的第']},
    vehicle: {future: ['距离爱车保养续保','平平安安安全驾驶','记得检查车况哦','爱车专属纪念'], past: ['爱车相伴的第','风雨同路的第','安全行驶的第','保驾护航的第']}
  }
  const catData = dict[categoryId] || {future: [], past: []}
  const pool = isPast ? [...catData.past, ...generalPast] : [...catData.future, ...generalFuture]
  let hash = new Date().getDate()
  for (let i = 0; i < itemId.length; i++) { hash += itemId.charCodeAt(i) }
  return pool[hash % pool.length]
}

// 5分类分享卡片配色
const SHARE_THEME = {
  birthday: {bg: '#1C0D00', num: '#FFE4B5', sub: 'rgba(255,228,181,0.7)', accent: '#D4A017', emoji: '🎂'},
  love: {bg: '#1A0515', num: '#FFB6C1', sub: 'rgba(255,182,193,0.7)', accent: '#E8719A', emoji: '💕'},
  wedding: {bg: '#FFFCF5', num: '#C9A96E', sub: 'rgba(139,115,85,0.8)', accent: '#C9A96E', emoji: '💒'},
  death: {bg: '#08081A', num: '#C8C8DC', sub: 'rgba(200,200,220,0.6)', accent: '#9090B0', emoji: '🙏', titleColor: '#E0E0EC'},
  pet_birthday: {bg: '#FFF8F0', num: '#C47830', sub: 'rgba(122,72,32,0.8)', accent: '#C47830', emoji: '🐾', titleColor: '#4A2810'},
  repayment: {bg: '#F5F8F6', num: '#78A090', sub: 'rgba(120,160,144,0.7)', accent: '#78A090', emoji: '💳', titleColor: '#2C3E30'},
  period: {bg: '#FFF5F6', num: '#B87888', sub: 'rgba(184,120,136,0.7)', accent: '#B87888', emoji: '🌸', titleColor: '#3E2028'},
  onboarding: {bg: '#F5F7F9', num: '#6890A8', sub: 'rgba(104,144,168,0.7)', accent: '#6890A8', emoji: '💼', titleColor: '#2A3E4E'},
  vehicle: {bg: '#F6F6F4', num: '#888A84', sub: 'rgba(136,138,132,0.7)', accent: '#888A84', emoji: '🚗', titleColor: '#2C2C28'},
  festival: {bg: '#FFF0E8', num: '#C04030', sub: 'rgba(192,64,48,0.7)', accent: '#C04030', emoji: '🎊', titleColor: '#5C1A10'}
}
function getShareTheme(catId) { return SHARE_THEME[catId] || SHARE_THEME.birthday }

function drawImageCover(ctx, imagePath, imageInfo, x, y, width, height) {
  if (!imageInfo || !imageInfo.width || !imageInfo.height) {
    ctx.drawImage(imagePath, x, y, width, height)
    return
  }

  const sourceRatio = imageInfo.width / imageInfo.height
  const targetRatio = width / height
  let sx = 0
  let sy = 0
  let sw = imageInfo.width
  let sh = imageInfo.height

  if (sourceRatio > targetRatio) {
    sw = imageInfo.height * targetRatio
    sx = (imageInfo.width - sw) / 2
  } else {
    sh = imageInfo.width / targetRatio
    sy = (imageInfo.height - sh) / 2
  }

  ctx.drawImage(imagePath, sx, sy, sw, sh, x, y, width, height)
}

function drawRoundRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2)
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + width - r, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + r)
  ctx.lineTo(x + width, y + height - r)
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height)
  ctx.lineTo(x + r, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - r)
  ctx.lineTo(x, y + r)
  ctx.quadraticCurveTo(x, y, x + r, y)
  ctx.closePath()
}

function hexToRgba(hex, alpha) {
  const normalized = String(hex || '').replace('#', '')
  if (normalized.length !== 6) return `rgba(205,231,255,${alpha})`
  const r = parseInt(normalized.slice(0, 2), 16)
  const g = parseInt(normalized.slice(2, 4), 16)
  const b = parseInt(normalized.slice(4, 6), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

function fillBlob(ctx, x, y, radius, color, alpha, scaleX = 1, scaleY = 1) {
  ctx.save && ctx.save()
  if (ctx.translate && ctx.scale) {
    ctx.translate(x, y)
    ctx.scale(scaleX, scaleY)
    const gradient = ctx.createCircularGradient
      ? ctx.createCircularGradient(0, 0, radius)
      : null
    if (gradient && gradient.addColorStop) {
      gradient.addColorStop(0, hexToRgba(color, alpha))
      gradient.addColorStop(0.52, hexToRgba(color, alpha * 0.54))
      gradient.addColorStop(1, hexToRgba(color, 0))
      ctx.setFillStyle(gradient)
      ctx.beginPath()
      ctx.arc(0, 0, radius, 0, Math.PI * 2)
      ctx.fill()
    } else {
      for (let i = 12; i >= 1; i -= 1) {
        const progress = i / 12
        ctx.beginPath()
        ctx.setGlobalAlpha(alpha * 0.05 * (1 - progress * 0.34))
        ctx.setFillStyle(color)
        ctx.arc(0, 0, radius * progress, 0, Math.PI * 2)
        ctx.fill()
      }
    }
  } else {
    const gradient = ctx.createCircularGradient
      ? ctx.createCircularGradient(x, y, radius)
      : null
    if (gradient && gradient.addColorStop) {
      gradient.addColorStop(0, hexToRgba(color, alpha))
      gradient.addColorStop(0.52, hexToRgba(color, alpha * 0.54))
      gradient.addColorStop(1, hexToRgba(color, 0))
      ctx.setFillStyle(gradient)
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
    } else {
      for (let i = 12; i >= 1; i -= 1) {
        const progress = i / 12
        ctx.beginPath()
        ctx.setGlobalAlpha(alpha * 0.05 * (1 - progress * 0.34))
        ctx.setFillStyle(color)
        ctx.arc(x, y, radius * progress, 0, Math.PI * 2)
        ctx.fill()
      }
    }
  }
  ctx.setGlobalAlpha(1)
  ctx.restore && ctx.restore()
}

function drawMistBackground(ctx, W, H, accent) {
  ctx.setFillStyle('#FAFCFF')
  ctx.fillRect(0, 0, W, H)

  fillBlob(ctx, -140, 10, 760, '#FBCFDE', 0.42, 1.24, 0.82)
  fillBlob(ctx, 1030, 90, 820, '#CDE7FF', 0.46, 1.08, 0.9)
  fillBlob(ctx, 160, 1160, 720, '#AEE7DE', 0.3, 1.32, 0.84)
  fillBlob(ctx, 960, 1130, 680, '#EFE1A9', 0.26, 1.2, 0.92)
  fillBlob(ctx, 540, 660, 760, accent, 0.18, 1.34, 0.78)
  fillBlob(ctx, 350, 350, 520, '#FFFFFF', 0.34, 1.64, 0.74)
  fillBlob(ctx, 770, 900, 620, '#FFFFFF', 0.3, 1.52, 0.78)

  ctx.setFillStyle('rgba(255,255,255,0.18)')
  ctx.fillRect(0, 0, W, H)
  ctx.setFillStyle('rgba(248,251,255,0.16)')
  ctx.fillRect(0, 0, W, H)
}

function fitFontSize(ctx, text, maxWidth, startSize, fontFamily, weight = 'normal') {
  let size = startSize
  while (size > 24) {
    ctx.font = `${weight} ${size}px ${fontFamily}`
    try {
      if (!ctx.measureText || ctx.measureText(text).width <= maxWidth) return size
    } catch (e) {
      return size
    }
    size -= 4
  }
  return size
}

function drawPosterOutput(ctx, W, H) {
  return new Promise((resolve, reject) => {
    let settled = false
    const finish = (fn) => {
      if (settled) return
      settled = true
      clearTimeout(timeoutTimer)
      fn()
    }
    const timeoutTimer = setTimeout(() => {
      finish(() => {
        wx.hideLoading()
        wx.showToast({title: '画报生成超时，请重试', icon: 'none'})
        reject(new Error('draw_timeout'))
      })
    }, 15000)

    try {
      // ⚠️ Canvas旧API：draw(false, callback) 在新版iOS基础库中已标记废弃
      // 后续版本应迁移到 Canvas 2D API: wx.createSelectorQuery().select('#shareCanvas').node()
      ctx.draw(false)
    } catch (err) {
      finish(() => {
        console.error('[detail] poster draw failed:', err)
        wx.hideLoading()
        wx.showToast({title: '画报生成失败，请重试', icon: 'none'})
        reject(err)
      })
      return
    }

    setTimeout(() => {
      wx.canvasToTempFilePath({
        canvasId: 'shareCanvas',
        x: 0, y: 0, width: W, height: H,
        destWidth: W, destHeight: H,
        fileType: 'jpg', quality: 1.0,
        success: (res) => {
          finish(() => {
            wx.hideLoading()
            const pages = getCurrentPages()
            const currentPage = pages[pages.length - 1]
            if (currentPage && currentPage.route === 'pages/detail/detail') {
              currentPage.setData({posterPreviewPath: res.tempFilePath})
            }
            wx.previewImage({
              urls: [res.tempFilePath],
              fail: err => {
                console.warn('[detail] previewImage failed, keep inline poster preview:', err)
              }
            })
            wx.showToast({title: '长按预览图即可保存', icon: 'none', duration: 2000})
            resolve(res.tempFilePath)
          })
        },
        fail: (err) => {
          finish(() => {
            console.error('[detail] poster export failed:', err)
            wx.hideLoading()
            wx.showToast({title: '画报生成失败，请重试', icon: 'none'})
            reject(err)
          })
        }
      })
    }, 900)
  })
}

function safeHideLoading() {
  try {
    wx.hideLoading()
  } catch (e) {
    // Loading may already be closed by another async branch.
  }
}

function getImageInfoWithTimeout(src, timeout = 1000) {
  return new Promise((resolve, reject) => {
    let settled = false
    const done = (fn) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      fn()
    }
    const timer = setTimeout(() => {
      done(() => reject(new Error(`get_image_info_timeout:${src}`)))
    }, timeout)

    wx.getImageInfo({
      src,
      success: res => done(() => resolve(res)),
      fail: err => done(() => reject(err))
    })
  })
}

const CATEGORY_EN_LABELS = {
  birthday: 'BIRTHDAY',
  love: 'LOVE',
  wedding: 'WEDDING',
  // ✅ P2#15: MEMORIAL → IN MEMORIAM（更正式的表达）
  death: 'IN MEMORIAM',
  festival: 'CUSTOM',
  repayment: 'PAYMENT',
  period: 'PERIOD',
  onboarding: 'CAREER',
  vehicle: 'INSURANCE',
  pet_birthday: 'PET BIRTHDAY'
}

Page({
  data: {
    statusBarHeight: 20,
    item: null,
    currentTheme: 'apple',
    theme: {},
    remindEnabled: false,
    id: null,
    posterPreviewPath: '',
    posterCanvasWidth: 1080,
    posterCanvasHeight: 1440
  },

  onLoad(options) {
    try {
      const windowInfo = wx.getWindowInfo()
      const menuButton = wx.getMenuButtonBoundingClientRect()
      const statusBarHeight = windowInfo.statusBarHeight || 20
      // 官方标准公式：导航栏高度 = (胶囊top - 状态栏) × 2 + 胶囊高度
      const navBarHeight = (menuButton.top - statusBarHeight) * 2 + menuButton.height

      this.setData({
        statusBarHeight,
        navBarHeight: Math.round(navBarHeight),
        totalTopHeight: Math.round(statusBarHeight + navBarHeight)
      })
    } catch(e) {
      this.setData({statusBarHeight: 20, navBarHeight: 44, totalTopHeight: 64})
    }

    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    this.setData({
      id: options.id,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
  },

  onShow() {
    this.loadItem()
    // ✅ WXS 接管倒计时动态显示，JS 层只需每30秒检查是否跨天
    this._startDayCheck()
  },

  onHide() { this._stopDayCheck() },
  onUnload() { this._stopDayCheck() },

  _startDayCheck() {
    this._stopDayCheck()
    this._dayCheckTimer = setInterval(() => {
      const now = new Date()
      const today = now.toDateString()
      if (this._lastToday && this._lastToday !== today) {
        this.loadItem()
      }
      this._lastToday = today
    }, 30000) // 30秒检查一次跨天
  },

  _stopDayCheck() {
    if (this._dayCheckTimer) { clearInterval(this._dayCheckTimer); this._dayCheckTimer = null }
  },

  // _refreshCountdown 已废弃：WXS 接管倒计时动态显示，详情页每秒 setData 已消除

  // uploadUserPhoto 已移除（UI已不用此功能）

  async loadItem() {
    if (this._redirectingToPeriod) return

    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    const items = await countdownStore.getItems()
    const raw = items.find(i => i.id === this.data.id)

    if (!raw) {
      wx.showToast({title: '未找到', icon: 'none'})
      setTimeout(() => { wx.navigateBack() }, 1000)
      return
    }

    // 姨妈日：跳转到专属追踪页面
    if (raw.categoryId === 'period') {
      this._redirectingToPeriod = true
      wx.redirectTo({url: `/pages/period/period?id=${this.data.id}`})
      return
    }

    const now = new Date()
    const cat = categories.getCategoryById(raw.categoryId)

    const itemData = {
      targetDate: raw.targetDate,
      isRecurring: raw.isRecurring ?? categories.isRecurringCategory(raw.categoryId),
      startDate: raw.startDate || raw.targetDate,
      direction: raw.direction || cat.direction
    }

    const main = countdown.getMainCountdown(itemData, now)
    const elapsed = countdown.getElapsedText(itemData, now)

    const hh = String(main.hours).padStart(2, '0')
    const mm = String(main.minutes).padStart(2, '0')
    const ss = String(main.seconds).padStart(2, '0')
    const fullCountdown = `${hh}:${mm}:${ss}`

    const heartCopy = copyTemplates.getCopy(
      raw.categoryId, elapsed.isPast, elapsed.totalDays, elapsed.years
    )

    let detailMain = ''
    let detailSub = heartCopy

    if (elapsed.isPast && itemData.isRecurring) {
      detailMain = `第 ${elapsed.totalDays} 天`
    } else if (main.isPast) {
      detailMain = `已过 ${main.days} 天`
      detailSub = heartCopy
    } else {
      detailMain = `还有 ${main.days} 天`
      detailSub = heartCopy
    }

    let headlineLabel = ''
    let headlineUnit = 'Days'

    if (elapsed.isPast && itemData.isRecurring) {
      headlineLabel = '又到了这一天'
      headlineUnit = 'Days'
    } else if (main.isPast) {
      headlineLabel = '已过去'
      headlineUnit = 'Days'
    } else {
      headlineLabel = '请怀期待'
      headlineUnit = 'Days'
    }

    const milestone = itemData.isRecurring
      ? null
      : countdown.getNextMilestone(raw.targetDate, main.isPast ? -main.days : main.days)

    // ✅ WXS 倒计时用：计算目标日次日00:00的毫秒时间戳
    let _nextTargetEndMs = 0
    if (itemData.direction !== 'countup') {
      const target = parseDateSafe(raw.targetDate)
      if (!isNaN(target.getTime())) {
        if (itemData.isRecurring) {
          const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
          const targetMonth = target.getMonth()
          const targetDay = target.getDate()
          const isLeap = (now.getFullYear() % 4 === 0 && now.getFullYear() % 100 !== 0) || now.getFullYear() % 400 === 0
          const anniversaryDay = (targetMonth === 1 && targetDay === 29 && !isLeap) ? 28 : targetDay
          let anniversary = new Date(now.getFullYear(), targetMonth, anniversaryDay)
          if (anniversary < todayStart) {
            const nextYear = now.getFullYear() + 1
            const nextIsLeap = (nextYear % 4 === 0 && nextYear % 100 !== 0) || nextYear % 400 === 0
            const nextDay = (targetMonth === 1 && targetDay === 29 && !nextIsLeap) ? 28 : targetDay
            anniversary = new Date(nextYear, targetMonth, nextDay)
          }
          _nextTargetEndMs = new Date(anniversary.getFullYear(), anniversary.getMonth(), anniversary.getDate() + 1).getTime()
        } else {
          _nextTargetEndMs = new Date(target.getFullYear(), target.getMonth(), target.getDate() + 1).getTime()
        }
      }
    }

    this.setData({
      item: {
        ...raw,
        isPast: main.isPast,
        preciseIsPast: main.isPast,
        statusText: getEmotionalStatus(raw.categoryId, main.isPast, raw.id.toString()),
        countdownPreciseDays: main.days,
        countdownPrecise: main.totalFormatted,
        countdownHms: fullCountdown,
        headlineLabel,
        headlineUnit,
        detailMain,
        detailSub: heartCopy,
        dateStr: this.formatDate(raw.targetDate),
        icon: cat.icon,
        name: cat.name,
        categoryLabelEn: CATEGORY_EN_LABELS[raw.categoryId] || String(cat.name || '').toUpperCase(),
        milestone: milestone
          ? `距离${milestone.milestone}天纪念日还有 ${milestone.daysLeft} 天`
          : null,
        isRecurring: itemData.isRecurring,
        direction: itemData.direction,
        startDate: itemData.startDate,
        _nextTargetEndMs  // WXS 倒计时用
      },
      remindEnabled: raw.remindDays >= 0,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })
  },

  formatDate(dateStr) {
    const d = parseDateSafe(dateStr)
    return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
  },

  goBack() {
    const pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.reLaunch({url: '/pages/index/index'})
    }
  },
  goToEdit() { wx.navigateTo({url: `/pages/add/add?id=${this.data.id}`}) },

  async toggleRemind() {
    try {
      const items = countdownStore.readLocalItems()
      const idx = items.findIndex(i => i.id === this.data.id)
      if (idx === -1) return
      const currentDays = items[idx].remindDays
      items[idx].remindDays = currentDays >= 0 ? -1 : 1
      const result = await countdownStore.saveItem(items[idx])
      this.setData({remindEnabled: items[idx].remindDays >= 0})
      wx.showToast({
        title: result.synced
          ? (items[idx].remindDays >= 0 ? '已开启提醒' : '已关闭提醒')
          : '已本地更新提醒',
        icon: 'none'
      })
    } catch(e) {
      console.error('[detail] toggleRemind failed:', e)
      wx.showToast({title: '提醒更新失败', icon: 'none'})
    }
  },

  previewCover() {
    if (this.data.item && this.data.item.coverImage) {
      wx.previewImage({urls: [this.data.item.coverImage], current: this.data.item.coverImage})
    }
  },

  previewPhoto() {
    if (this.data.item && this.data.item.userPhoto) {
      wx.previewImage({urls: [this.data.item.userPhoto], current: this.data.item.userPhoto})
    }
  },

  shareCard() {
    const item = this.data.item
    if (!item) return

    wx.showActionSheet({
      itemList: item.coverImage ? ['使用当前封面生成', '上传新照片生成'] : ['上传照片生成', '直接生成简约画报'],
      success: (res) => {
        if ((item.coverImage && res.tapIndex === 1) || (!item.coverImage && res.tapIndex === 0)) {
          this.pickImageForShare()
        } else {
          this.drawFinalPoster(item.coverImage)
        }
      }
    })
  },

  pickImageForShare() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        getImageInfoWithTimeout(tempFilePath, 3000)
          .then((info) => {
            const screenWidth = wx.getSystemInfoSync().windowWidth
            const realCropHeight = Math.round(screenWidth * (900 / 960))
            const displayHeight = (info.height / info.width) * screenWidth
            const maxTop = Math.max(0, displayHeight - realCropHeight)

            this.setData({
              showShareCropper: true,
              cropImagePath: tempFilePath,
              imageWidth: info.width,
              imageHeight: info.height,
              cropFrameHeight: realCropHeight,
              cropFrameTop: maxTop / 2
            })
          })
          .catch((err) => {
            console.error('[detail] choose image info failed:', err)
            wx.showToast({title: '图片读取失败，请重试', icon: 'none'})
          })
      }
    })
  },

  cancelShareCrop() {
    this.setData({showShareCropper: false, cropImagePath: ''})
  },

  onCropTouchStart(e) {
    this.setData({grabOffset: e.touches[0].clientY - this.data.cropFrameTop})
  },

  onCropTouchMove(e) {
    const touchY = e.touches[0].clientY
    const screenWidth = wx.getSystemInfoSync().windowWidth
    const displayHeight = (this.data.imageHeight / this.data.imageWidth) * screenWidth
    const maxTop = Math.max(0, displayHeight - this.data.cropFrameHeight)
    let newTop = touchY - this.data.grabOffset
    newTop = Math.max(0, Math.min(maxTop, newTop))
    this.setData({cropFrameTop: newTop})
  },

  preventTouch(_e) {},

  closePosterPreview() {
    this.setData({posterPreviewPath: ''})
  },

  previewGeneratedPoster() {
    if (!this.data.posterPreviewPath) return
    wx.previewImage({urls: [this.data.posterPreviewPath]})
  },

  confirmShareCrop() {
    wx.showLoading({title: '处理中...', mask: true})
    const ctx = wx.createCanvasContext('cropCanvas')
    const screenW = wx.getSystemInfoSync().windowWidth
    const scale = this.data.imageWidth / screenW
    const cropY = Math.round(this.data.cropFrameTop * scale)
    const cropH = Math.round(this.data.cropFrameHeight * scale)

    this.setData({canvasWidth: screenW, canvasHeight: this.data.cropFrameHeight})

    const exportCrop = () => {
      let settled = false
      const finish = (fn) => {
        if (settled) return
        settled = true
        clearTimeout(timeoutTimer)
        fn()
      }
      const timeoutTimer = setTimeout(() => {
        finish(() => {
          wx.hideLoading()
          wx.showToast({title: '图片处理超时，请重试', icon: 'none'})
        })
      }, 6000)

      try {
        ctx.draw(false)
      } catch (err) {
        finish(() => {
          console.error('[detail] crop draw failed:', err)
          wx.hideLoading()
          wx.showToast({title: '图片处理失败，请重试', icon: 'none'})
        })
        return
      }

      setTimeout(() => {
        wx.canvasToTempFilePath({
          canvasId: 'cropCanvas',
          x: 0, y: 0, width: screenW, height: this.data.cropFrameHeight,
          destWidth: screenW, destHeight: this.data.cropFrameHeight,
          fileType: 'jpg', quality: 0.8,
          success: (res) => {
            finish(() => {
              wx.hideLoading()
              this.setData({showShareCropper: false})
              this.drawFinalPoster(res.tempFilePath)
            })
          },
          fail: (err) => {
            finish(() => {
              console.error('[detail] crop export failed:', err)
              wx.hideLoading()
              wx.showToast({title: '图片处理失败，请重试', icon: 'none'})
            })
          }
        })
      }, 500)
    }

    setTimeout(() => {
      ctx.drawImage(this.data.cropImagePath, 0, cropY, this.data.imageWidth, cropH, 0, 0, screenW, this.data.cropFrameHeight)
      exportCrop()
    }, 200)
  },

  drawFinalPoster(imageUrl) {
    wx.showLoading({title: '正在冲印画报...', mask: true})
    const item = this.data.item
    if (!item) {
      safeHideLoading()
      wx.showToast({title: '画报数据异常，请重试', icon: 'none'})
      return
    }

    const W = 1080, H = 1440
    this.setData({
      posterCanvasWidth: W,
      posterCanvasHeight: H,
      posterPreviewPath: ''
    })

    const ctx = wx.createCanvasContext('shareCanvas')
    const st = getShareTheme(item.categoryId)

    const drawCountBlock = (rightX, labelY, countY, metaY) => {
      ctx.setTextAlign('right')
      ctx.setFillStyle('#8C8070')
      ctx.font = 'normal 30px "PingFang SC", sans-serif'
      const posterCountLabel = item.preciseIsPast
        ? (item.direction === 'countup' ? '已累计' : '已经过去')
        : `距离 ${item.title} 还有`
      ctx.fillText(posterCountLabel, rightX, labelY)

      ctx.setFillStyle('#1A1A1A')
      ctx.font = 'normal 104px "Helvetica Neue", sans-serif'
      ctx.fillText(String(item.countdownPreciseDays), rightX - 286, countY)
      ctx.font = 'normal 100px "Helvetica Neue", sans-serif'
      ctx.fillText('DAYS', rightX, countY)

      ctx.setFillStyle('#8C8070')
      ctx.font = 'normal 26px "PingFang SC", sans-serif'
      ctx.fillText(`${st.emoji} ${item.name} | ${item.statusText} | ISO 2026`, rightX, metaY)
    }

    const renderSimplePosterClassic = () => {
      const accent = st.accent || '#D8C2AD'
      const titleColor = st.titleColor || '#243247'
      drawMistBackground(ctx, W, H, accent)

      const cardX = 90, cardY = 180, cardW = 900, cardH = 1040
      drawRoundRect(ctx, cardX, cardY, cardW, cardH, 72)
      ctx.setFillStyle('rgba(255,255,255,0.5)')
      ctx.fill()
      ctx.save && ctx.save()
      drawRoundRect(ctx, cardX, cardY, cardW, cardH, 72)
      ctx.clip && ctx.clip()
      fillBlob(ctx, cardX + 34, cardY + 40, 460, '#FBCFDE', 0.18, 1.34, 0.62)
      fillBlob(ctx, cardX + cardW - 28, cardY + 36, 500, '#CDE7FF', 0.2, 1.26, 0.62)
      fillBlob(ctx, cardX + 110, cardY + cardH - 24, 460, '#AEE7DE', 0.16, 1.34, 0.58)
      fillBlob(ctx, cardX + cardW - 120, cardY + cardH - 10, 420, '#EFE1A9', 0.13, 1.2, 0.58)
      fillBlob(ctx, cardX + cardW / 2, cardY + cardH / 2, 560, accent, 0.08, 1.28, 0.7)
      ctx.setFillStyle('rgba(255,255,255,0.34)')
      ctx.fillRect(cardX, cardY, cardW, cardH)
      ctx.restore && ctx.restore()
      drawRoundRect(ctx, cardX, cardY, cardW, cardH, 72)
      ctx.setStrokeStyle('rgba(255,255,255,0.86)')
      ctx.setLineWidth(3)
      ctx.stroke()

      ctx.setTextAlign('center')
      drawRoundRect(ctx, cardX + 300, cardY + 78, 300, 70, 35)
      ctx.setFillStyle('rgba(255,255,255,0.62)')
      ctx.fill()
      ctx.setFillStyle(accent)
      ctx.font = 'bold 28px "SF Pro Text", "PingFang SC", sans-serif'
      ctx.fillText(item.categoryLabelEn || item.name || 'NO FORGET', cardX + cardW / 2, cardY + 124)

      ctx.setFillStyle(titleColor)
      ctx.font = 'bold 58px "PingFang SC", sans-serif'
      ctx.fillText(item.title, cardX + cardW / 2, cardY + 260)
      ctx.setFillStyle('#8C99AD')
      ctx.font = 'normal 26px "SF Pro Text", "PingFang SC", sans-serif'
      ctx.fillText(item.dateStr, cardX + cardW / 2, cardY + 310)

      ctx.setTextAlign('center')
      ctx.setFillStyle(titleColor)
      ctx.font = 'normal 30px "PingFang SC", sans-serif'
      const posterCountLabel = item.preciseIsPast
        ? (item.direction === 'countup' ? '已累计' : '已经过去')
        : `距离 ${item.title} 还有`
      ctx.fillText(posterCountLabel, cardX + cardW / 2, cardY + 445)

      ctx.setFillStyle(accent)
      ctx.font = 'normal 190px "Helvetica Neue", sans-serif'
      ctx.fillText(String(item.countdownPreciseDays), cardX + cardW / 2, cardY + 620)
      ctx.font = 'normal 52px "Helvetica Neue", sans-serif'
      ctx.fillText('DAYS', cardX + cardW / 2, cardY + 690)

      ctx.setFillStyle(titleColor)
      ctx.font = 'normal 30px "PingFang SC", sans-serif'
      ctx.fillText(item.statusText, cardX + cardW / 2, cardY + 800)
      ctx.setFillStyle(accent)
      ctx.font = 'italic 32px "Songti SC", serif'
      ctx.fillText(`" ${item.detailSub} "`, cardX + cardW / 2, cardY + 872)

      ctx.setTextAlign('center')
      ctx.setFillStyle('#B7C0CF')
      ctx.font = 'bold 24px "SF Pro Text", "PingFang SC", sans-serif'
      ctx.fillText('NO FORGET · 记住每一个重要时刻', cardX + cardW / 2, cardY + 965)

      drawPosterOutput(ctx, W, H).catch(err => {
        console.error('[detail] simple poster output failed:', err)
      })
    }

    const render = (imageInfo) => {
      ctx.setFillStyle('#FFFFFF')
      ctx.fillRect(0, 0, W, H)

      const imgX = 60, imgY = 230, imgW = 960, imgH = 900

      ctx.setTextAlign('left')
      ctx.setFillStyle('#1A1A1A')
      ctx.font = 'bold 64px "PingFang SC", sans-serif'
      ctx.fillText(item.title, imgX, 120)

      ctx.setFillStyle('#A49D93')
      ctx.font = '300 24px "SF Pro Text", sans-serif'
      ctx.fillText(`PHOTOGRAPHED IN : ${item.dateStr.replace(/\./g, ' / ')}`, imgX, 170)

      if (imageUrl) {
        drawImageCover(ctx, imageUrl, imageInfo, imgX, imgY, imgW, imgH)
        ctx.setStrokeStyle('rgba(0,0,0,0.05)')
        ctx.setLineWidth(2)
        ctx.strokeRect(imgX, imgY, imgW, imgH)
      } else {
        ctx.setFillStyle(st.bg || '#F5F5F5')
        ctx.fillRect(imgX, imgY, imgW, imgH)
      }

      const rightX = imgX + imgW

      drawCountBlock(rightX, 1178, 1282, 1332)

      ctx.setFillStyle(st.accent || '#D8C2AD')
      ctx.font = 'italic 28px "Songti SC", serif'
      ctx.fillText(`" ${item.detailSub} "`, rightX, 1364)

      ctx.setTextAlign('left')
      ctx.setFillStyle('#C2BCB4')
      ctx.font = 'bold 24px "SF Pro Text", "PingFang SC", sans-serif'
      ctx.fillText('NO FORGET · 记住每一个重要时刻', imgX, 1364)

      drawPosterOutput(ctx, W, H).catch(err => {
        console.error('[detail] image poster output failed:', err)
      })
    }

    try {
      if (!imageUrl) {
        renderSimplePosterClassic()
        return
      }

      getImageInfoWithTimeout(imageUrl, 5000)
        .then(render)
        .catch((err) => {
          console.warn('[detail] poster image info unavailable, render without image:', err)
          render(null)
        })
    } catch (err) {
      console.error('[detail] poster generation failed before output:', err)
      safeHideLoading()
      wx.showToast({title: '画报生成失败，请重试', icon: 'none'})
    }
  },

  savePosterToAlbum(filePath) {
    wx.saveImageToPhotosAlbum({
      filePath: filePath,
      success: () => wx.showToast({title: '已保存', icon: 'success'})
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