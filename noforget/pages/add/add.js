// pages/add/add.js - 添加/编辑页面逻辑 v2
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const {getIconPath} = require('../../utils/icons.js')
const countdownStore = require('../../utils/countdownStore.js')
const periodUtil = require('../../utils/period.js')
const periodCloud = require('../../utils/periodCloud.js')

const CATEGORY_EN_LABELS = {
  period: 'LUNA',
  birthday: 'BIRTHDAY',
  love: 'LOVE',
  repayment: 'PAYMENT',
  vehicle: 'INSURANCE',
  pet_birthday: 'PET',
  wedding: 'WEDDING',
  onboarding: 'CAREER',
  festival: 'CUSTOM',
  death: 'MEMORIAL'
}

Page({
  data: {
    statusBarHeight: 20,
    title: '',
    targetDate: '',
    selectedCategory: 'birthday',
    categoryId: 'birthday',
    remindDays: 1,
    categories: [],
    theme: {},
    currentTheme: 'apple',
    isEdit: false,
    editId: null,
    mode: 'future',

    // 预览数据
    previewCountdownDays: 0,
    previewCountdownHms: '00:00:00',
    previewPreciseIsPast: false,
    previewIconPath: '',
    previewIcon: '🎂',
    previewCategoryEn: 'BIRTHDAY',
    previewCategoryName: '生日',

    // 封面图片
    coverImage: '',

    // 裁切相关
    showCropper: false,
    cropImagePath: '',
    imageHeight: 0,
    imageWidth: 0,
    cropFrameTop: 0,
    cropFrameHeight: 240,
    grabOffset: 0,
    frameStartY: 0,

    // 防双击标记
    _saving: false
  },

  computeCategories(currentTheme) {
    return categories.getAllCategories().map(cat => ({
      ...cat,
      labelEn: CATEGORY_EN_LABELS[cat.id] || String(cat.name || '').toUpperCase(),
      iconPath: getIconPath(currentTheme, cat.id)
    }))
  },

  onLoad(options) {
    console.log('[add] onLoad:start', options || {})
    const windowInfo = wx.getWindowInfo()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'

    this.setData({
      statusBarHeight: windowInfo.statusBarHeight || 20,
      currentTheme,
      theme: app.globalData.themes[currentTheme],
      categories: this.computeCategories(currentTheme),
      selectedCategory: 'birthday',
      previewIconPath: getIconPath(currentTheme, 'birthday'),
      previewCategoryEn: CATEGORY_EN_LABELS.birthday,
      previewCategoryName: '生日'
    })

    if (options.id) {
      this.setData({isEdit: true, editId: options.id})
      this.loadItem(options.id)
    }
    console.log('[add] onLoad:end')
  },

  async loadItem(id) {
    const items = await countdownStore.getItems()
    const item = items.find(i => i.id === id)
    if (!item) return

    // ★ 完整加载所有字段（编辑时需要完整保留）
      this.setData({
        title: item.title,
        targetDate: (item.targetDate || '').split(' ')[0],
        selectedCategory: item.categoryId,
        categoryId: item.categoryId,
        mode: item.direction === 'countup' ? 'past' : 'future',
        remindDays: item.remindDays || 1,
        coverImage: item.coverImage || '',
        previewIconPath: getIconPath(this.data.currentTheme, item.categoryId),
        previewCategoryEn: CATEGORY_EN_LABELS[item.categoryId] || '',
        previewCategoryName: categories.getCategoryById(item.categoryId)?.name || '',
        _storedIsRecurring: item.isRecurring,
        _storedDirection: item.direction,
        _storedStartDate: item.startDate
      })
    this.updatePreview()
  },

  onTitleInput(e) {
    this.setData({title: e.detail.value})
    this.updatePreview()
  },

  onDateChange(e) {
    this.setData({targetDate: e.detail.value})
    this.updatePreview()
  },

  selectCategory(e) {
    wx.vibrateShort({type: 'light'})
    const catId = e.currentTarget.dataset.id
    this.setData({
      selectedCategory: catId,
      categoryId: catId,
      previewIconPath: getIconPath(this.data.currentTheme, catId),
      previewCategoryEn: CATEGORY_EN_LABELS[catId] || '',
      previewCategoryName: categories.getCategoryById(catId)?.name || '',
      coverImage: catId === 'period' ? '' : this.data.coverImage
    })
    this.updatePreview()
  },

  // --- 🌟 新增：一键切换时间模式（用交互教用户） ---
  switchToFuture() {
    wx.vibrateShort({type: 'light'})
    this.setData({mode: 'future'})
    this.updatePreview()
  },

  switchToPast() {
    wx.vibrateShort({type: 'light'})
    this.setData({mode: 'past'})
    this.updatePreview()
  },
  // ----------------------------------------------

  setRemind(e) {
    wx.vibrateShort({type: 'light'})
    this.setData({remindDays: parseInt(e.currentTarget.dataset.days)})
  },

  // ★ 核心：预览使用新的双函数计算（含startDate透传）
  updatePreview() {
    if (!this.data.targetDate) {
      this.setData({
        previewCountdownDays: 0,
        previewCountdownHms: '00:00:00',
        previewPreciseIsPast: false
      })
      return
    }
    const now = new Date()
    const cat = categories.getCategoryById(this.data.selectedCategory) || {icon: '✨', isRecurring: false, direction: 'up'}
    const mode = this.data.mode || 'future'

    const previewItem = {
      targetDate: this.data.targetDate,
      isRecurring: mode === 'future' ? !!cat.isRecurring : false,
      direction: mode === 'past' ? 'countup' : (cat.direction || 'up'),
      startDate: this.data.targetDate
    }

    const mainCountdown = countdown.getMainCountdown(previewItem, now) || {totalFormatted: '0 00:00:00', days: 0, isPast: false}
    const hmsPart = (mainCountdown.totalFormatted && mainCountdown.totalFormatted.split(' ')[1]) || '00:00:00'

    this.setData({
      previewCountdownDays: mainCountdown.days || 0,
      previewCountdownHms: hmsPart,
      previewPreciseIsPast: mainCountdown.isPast || false,
      previewIcon: cat.icon,
      previewCategoryEn: CATEGORY_EN_LABELS[this.data.selectedCategory] || '',
      previewCategoryName: cat.name || ''
    })
  },

  // ★ 核心：saveItem 完整保存所有字段（含云端同步）
  async saveItem() {
    if (this._saving) return
    if (this.data.selectedCategory !== 'period' && !this.data.title.trim()) {
      wx.showToast({title: '请输入名称', icon: 'none'})
      return
    }
    if (!this.data.targetDate) {
      wx.showToast({title: '请选择日期', icon: 'none'})
      return
    }
    this._saving = true

    try {
      wx.showLoading({title: '保存中...', mask: true})

      if (this.data.selectedCategory === 'period') {
        const existingEntries = periodUtil.getEntries()
        const duplicate = existingEntries.find(entry => entry.startDate === this.data.targetDate)
        if (duplicate && !this.data.isEdit) {
          wx.hideLoading()
          wx.showToast({title: '该日期已记录', icon: 'none'})
          return
        }

        if (this.data.isEdit) {
          const items = await countdownStore.getItems() || []
          const currentItem = items.find(i => i.id === this.data.editId)
          if (currentItem && currentItem.categoryId === 'period') {
            // ★ 修复：先尝试添加新记录，成功后再删除旧记录（避免非原子操作丢数据）
            const addResult = periodUtil.addEntry({startDate: this.data.targetDate})
            if (!addResult.success && addResult.reason !== 'duplicate') {
              throw new Error('period-entry-save-failed')
            }
            if (addResult.success) {
              await countdownStore.removeItem(currentItem.id)
            }
            // addEntry 成功后继续后续流程
            const periodItem = {
              id: 'period-item',
              title: this.data.title.trim() || '姨妈追踪',
              targetDate: this.data.targetDate,
              categoryId: 'period',
              isPeriod: true,
              createdAt: Date.now(),
              updatedAt: Date.now()
            }
            await countdownStore.saveItem(periodItem)
            periodCloud.scheduleSync(periodUtil.getEntries(), periodUtil.getDailyRecords(), periodUtil.getSettings())
            wx.hideLoading()
            wx.showToast({title: '已更新追踪', icon: 'success'})
            setTimeout(() => { wx.navigateBack() }, 800)
            return
          }
        }

        const addResult = periodUtil.addEntry({startDate: this.data.targetDate})
        if (!addResult.success && addResult.reason !== 'duplicate') {
          throw new Error('period-entry-save-failed')
        }

        const periodItem = {
          id: 'period-item',
          title: this.data.title.trim() || '姨妈追踪',
          targetDate: this.data.targetDate,
          categoryId: 'period',
          isPeriod: true,
          createdAt: Date.now(),
          updatedAt: Date.now()
        }
        await countdownStore.saveItem(periodItem)
        periodCloud.scheduleSync(periodUtil.getEntries(), periodUtil.getDailyRecords(), periodUtil.getSettings())

        wx.hideLoading()
        wx.showToast({title: '已开始追踪', icon: 'success'})
        setTimeout(() => { wx.navigateBack() }, 800)
        return
      }

      const items = await countdownStore.getItems() || []
      const cat = categories.getCategoryById(this.data.selectedCategory) || {}

      // 🌟 修复报错源：安全获取副标题
      let subtitle = '满怀期待'
      if (categories.pickSubtitle) {
        subtitle = categories.pickSubtitle(this.data.selectedCategory)
      } else if (cat.subtitles && cat.subtitles.length > 0) {
        subtitle = cat.subtitles[0]
      }

      // ★ 完整数据模型，增加所有潜在缺失字段的默认值
      const newItem = {
        id: this.data.isEdit ? this.data.editId : Date.now().toString(),
        title: this.data.title.trim(),
        targetDate: this.data.targetDate,
        categoryId: this.data.selectedCategory || 'default',
        remindDays: this.data.remindDays || 1,
        icon: cat.icon || '✨',
        coverImage: this.data.coverImage || '',

        // 编辑时保留原始字段，新建时用表单默认
        isRecurring: this.data.isEdit
          ? (this.data._storedIsRecurring !== undefined ? this.data._storedIsRecurring : !!cat.isRecurring)
          : (this.data.mode === 'future' ? !!cat.isRecurring : false),
        startDate: this.data.isEdit
          ? (this.data._storedStartDate || this.data.targetDate)
          : this.data.targetDate,
        direction: this.data.isEdit
          ? (this.data._storedDirection || cat.direction || 'up')
          : (this.data.mode === 'past' ? 'countup' : (cat.direction || 'up')),
        cardSubtitle: subtitle,

        createdAt: this.data.isEdit
          ? (items.find(i => i.id === this.data.editId)?.createdAt || Date.now())
          : Date.now(),
        updatedAt: Date.now()
      }

      // 1. 保存本地
      const result = await countdownStore.saveItem(newItem)

      wx.hideLoading()
      wx.showToast({
        title: (result && result.synced)
          ? (this.data.isEdit ? '已更新' : '已保存')
          : '已保存到本地',
        icon: 'success'
      })

      setTimeout(() => { wx.navigateBack() }, 1000)

    } catch (error) {
      wx.hideLoading()
      console.error('[add] saveItem 发生异常:', error)
      wx.showToast({title: '保存失败，请重试', icon: 'none'})
    } finally {
      this._saving = false
    }
  },

  requestRemindPermission(_item) {
    wx.showModal({
      title: '开启提醒',
      content: '开启后，纪念日当天或前一天会通过微信给你发送提醒',
      confirmText: '开启',
      cancelText: '暂不需要',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({title: '已开启提醒', icon: 'success'})
        }
      }
    })
  },

  async deleteItem() {
    if (this._deleting) return
    this._deleting = true
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除吗？',
      confirmColor: '#FF3B30',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({title: '删除中...', mask: true})
            const result = await countdownStore.removeItem(this.data.editId)
            wx.hideLoading()
            wx.showToast({
              title: result.synced ? '已删除' : '已本地删除',
              icon: 'success'
            })
            setTimeout(() => { wx.reLaunch({url: '/pages/index/index'}) }, 800)
          } catch(e) {
            wx.hideLoading()
            console.error('[add] deleteItem failed:', e)
            wx.showToast({title: '删除失败，请重试', icon: 'none'})
          }
        }
      },
      complete: () => {
        // ★ 修复：cancel/complete 都重置，防止 _deleting 永久锁死
        this._deleting = false
      }
    })
  },

  goBack() {
    const pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.reLaunch({url: '/pages/index/index'})
    }
  },

  // ==================== 封面裁切 ====================
  pickCoverImage() {
    wx.vibrateShort({type: 'medium'})
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        wx.getImageInfo({
          src: tempFilePath,
          success: (info) => {
            const screenWidth = wx.getSystemInfoSync().windowWidth
            // 🌟 核心修复：动态计算裁切高度，匹配详情页 650rpx 展示区域
            const realCropHeight = Math.round(screenWidth * (650 / 750))
            const displayHeight = (info.height / info.width) * screenWidth
            const maxTop = Math.max(0, displayHeight - realCropHeight)
            this.setData({
              showCropper: true,
              cropImagePath: tempFilePath,
              imageWidth: info.width,
              imageHeight: info.height,
              cropFrameHeight: realCropHeight,
              cropFrameTop: maxTop / 2
            })
          },
          fail: () => {
            this.setData({showCropper: true, cropImagePath: tempFilePath, cropFrameTop: 0})
          }
        })
      }
    })
  },

  cancelCrop() {
    wx.vibrateShort({type: 'light'})
    this.setData({showCropper: false, cropImagePath: '', cropFrameTop: 0})
  },

  onCropTouchStart(e) {
    const touchY = e.touches[0].clientY
    const frameTop = this.data.cropFrameTop
    this.setData({
      grabOffset: touchY - frameTop,
      frameStartY: frameTop
    })
  },

  onCropTouchMove(e) {
    const touchY = e.touches[0].clientY
    const screenWidth = wx.getSystemInfoSync().windowWidth
    const displayHeight = this.data.imageHeight && this.data.imageWidth
      ? (this.data.imageHeight / this.data.imageWidth) * screenWidth
      : screenWidth * 1.5
    const maxTop = Math.max(0, displayHeight - this.data.cropFrameHeight)
    let newTop = touchY - this.data.grabOffset
    newTop = Math.max(0, Math.min(maxTop, newTop))
    this.setData({cropFrameTop: newTop})
  },

  onCropTouchEnd() {},

  confirmCrop() {
    wx.showLoading({title: '处理中...'})
    const ctx = wx.createCanvasContext('cropCanvas')
    const screenWidth = wx.getSystemInfoSync().windowWidth
    const displayHeight = this.data.imageHeight && this.data.imageWidth
      ? (this.data.imageHeight / this.data.imageWidth) * screenWidth
      : screenWidth
    const scale = this.data.imageWidth / screenWidth
    const cropY = Math.round(this.data.cropFrameTop * scale)
    const cropH = Math.round(this.data.cropFrameHeight * scale)

    this.setData({canvasWidth: screenWidth, canvasHeight: this.data.cropFrameHeight})

    setTimeout(() => {
      ctx.drawImage(this.data.cropImagePath, 0, cropY, this.data.imageWidth, cropH, 0, 0, screenWidth, this.data.cropFrameHeight)
      ctx.draw(false, () => {
        wx.canvasToTempFilePath({
          canvasId: 'cropCanvas',
          x: 0, y: 0,
          width: screenWidth, height: this.data.cropFrameHeight,
          destWidth: screenWidth, destHeight: this.data.cropFrameHeight,
          fileType: 'jpg', quality: 0.6,
          success: (res) => {
            wx.hideLoading()
            this.setData({coverImage: res.tempFilePath, showCropper: false})
          },
          fail: () => {
            wx.hideLoading()
            this.setData({coverImage: this.data.cropImagePath, showCropper: false})
            wx.showToast({title: '裁切失败，使用原图', icon: 'none'})
          }
        })
      })
    }, 100)
  },

  removeCoverImage() {
    wx.showModal({
      title: '移除封面',
      content: '确定要移除封面照片吗？',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) this.setData({coverImage: ''})
      },
    })
  },

  preventTouch(e) {},

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
