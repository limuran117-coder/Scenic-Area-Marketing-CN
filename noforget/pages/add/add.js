// pages/add/add.js - 添加/编辑页面逻辑 v2
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')
const { getIconPath } = require('../../utils/icons.js')

Page({
  data: {
    statusBarHeight: 20,
    title: '',
    targetDate: '',
    selectedCategory: 'birthday',
    remindDays: 1,
    categories: [],
    theme: {},
    currentTheme: 'apple',
    isEdit: false,
    editId: null,

    // 预览数据
    previewCountdownDays: 0,
    previewCountdownHms: '00:00:00',
    previewPreciseIsPast: false,
    previewIconPath: '',
    previewIcon: '🎂',

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
    frameStartY: 0
  },

  computeCategories(currentTheme) {
    return categories.getAllCategories().map(cat => ({
      ...cat,
      iconPath: getIconPath(currentTheme, cat.id)
    }))
  },

  onLoad(options) {
    const systemInfo = wx.getSystemInfoSync()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'

    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 20,
      currentTheme,
      theme: app.globalData.themes[currentTheme],
      categories: this.computeCategories(currentTheme),
      selectedCategory: 'birthday',
      previewIconPath: getIconPath(currentTheme, 'birthday')
    })

    if (options.id) {
      this.setData({ isEdit: true, editId: options.id })
      this.loadItem(options.id)
    }
  },

  loadItem(id) {
    const items = wx.getStorageSync('countdownItems') || []
    const item = items.find(i => i.id === id)
    if (!item) return

    const cat = categories.getCategoryById(item.categoryId)
    // ★ 完整加载所有字段（编辑时需要完整保留）
    this.setData({
      title: item.title,
      targetDate: item.targetDate.split(' ')[0],
      selectedCategory: item.categoryId,
      remindDays: item.remindDays || 1,
      coverImage: item.coverImage || '',
      previewIconPath: getIconPath(this.data.currentTheme, item.categoryId)
      // isRecurring/direction/startDate 不改变，但数据已保存在 item 里
    })
    this.updatePreview()
  },

  onTitleInput(e) {
    this.setData({ title: e.detail.value })
    this.updatePreview()
  },

  onDateChange(e) {
    this.setData({ targetDate: e.detail.value })
    this.updatePreview()
  },

  selectCategory(e) {
    const catId = e.currentTarget.dataset.id
    this.setData({
      selectedCategory: catId,
      previewIconPath: getIconPath(this.data.currentTheme, catId)
    })
    this.updatePreview()
  },

  setRemind(e) {
    this.setData({ remindDays: parseInt(e.currentTarget.dataset.days) })
  },

  // ★ 核心：预览使用新的双函数计算（含startDate透传）
  updatePreview() {
    if (!this.data.targetDate) return
    const now = new Date()
    const cat = categories.getCategoryById(this.data.selectedCategory)

    // ★ 构建完整预览item（含startDate，getMainCountdown只需要targetDate/isRecurring/direction）
    const previewItem = {
      targetDate: this.data.targetDate,
      isRecurring: cat.isRecurring,
      direction: cat.direction,
      startDate: this.data.targetDate   // 默认startDate=targetDate，后续可扩展为用户自定义
    }

    const mainCountdown = countdown.getMainCountdown(previewItem, now)
    const elapsed = countdown.getElapsedText(previewItem, now)

    const hmsPart = (mainCountdown.totalFormatted.split(' ')[1] || '00:00:00')

    this.setData({
      previewCountdownDays: mainCountdown.days,
      previewCountdownHms: hmsPart,
      previewPreciseIsPast: mainCountdown.isPast,
      previewIcon: cat.icon
    })
  },

  // ★ 核心：saveItem 完整保存所有字段
  saveItem() {
    if (!this.data.title.trim()) {
      wx.showToast({ title: '请输入名称', icon: 'none' })
      return
    }
    if (!this.data.targetDate) {
      wx.showToast({ title: '请选择日期', icon: 'none' })
      return
    }

    const items = wx.getStorageSync('countdownItems') || []
    const cat = categories.getCategoryById(this.data.selectedCategory)

    // ★ 完整数据模型（含所有新字段）
    const newItem = {
      id: this.data.isEdit ? this.data.editId : Date.now().toString(),
      title: this.data.title.trim(),
      targetDate: this.data.targetDate,
      categoryId: this.data.selectedCategory,
      remindDays: this.data.remindDays,
      icon: cat.icon,
      coverImage: this.data.coverImage,

      // ★ 新增核心字段
      isRecurring: cat.isRecurring,     // 自动从分类判断
      startDate: this.data.targetDate,  // 默认=targetDate
      direction: cat.direction,          // 保留旧字段，向后兼容

      createdAt: this.data.isEdit
        ? items.find(i => i.id === this.data.editId)?.createdAt
        : Date.now(),
      updatedAt: Date.now()
    }

    if (this.data.isEdit) {
      const index = items.findIndex(i => i.id === this.data.editId)
      if (index > -1) items[index] = newItem
    } else {
      items.push(newItem)
    }

    wx.setStorageSync('countdownItems', items)

    wx.showToast({
      title: this.data.isEdit ? '已更新' : '已保存',
      icon: 'success'
    })

    setTimeout(() => { wx.navigateBack() }, 1000)
  },

  requestRemindPermission(item) {
    wx.showModal({
      title: '开启提醒',
      content: '开启后，纪念日当天或前一天会通过微信给你发送提醒',
      confirmText: '开启',
      cancelText: '暂不需要',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({ title: '已开启提醒', icon: 'success' })
        }
      }
    })
  },

  deleteItem() {
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除吗？',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          const items = wx.getStorageSync('countdownItems') || []
          const filtered = items.filter(i => i.id !== this.data.editId)
          wx.setStorageSync('countdownItems', filtered)
          wx.showToast({ title: '已删除', icon: 'success' })
          setTimeout(() => { wx.navigateBack() }, 1000)
        }
      }
    })
  },

  goBack() {
    wx.navigateBack()
  },

  // ==================== 封面裁切 ====================
  pickCoverImage() {
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
            const displayHeight = (info.height / info.width) * screenWidth
            const maxTop = Math.max(0, displayHeight - this.data.cropFrameHeight)
            this.setData({
              showCropper: true,
              cropImagePath: tempFilePath,
              imageWidth: info.width,
              imageHeight: info.height,
              cropFrameTop: maxTop / 2
            })
          },
          fail: () => {
            this.setData({ showCropper: true, cropImagePath: tempFilePath, cropFrameTop: 0 })
          }
        })
      }
    })
  },

  cancelCrop() {
    this.setData({ showCropper: false, cropImagePath: '', cropFrameTop: 0 })
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
    this.setData({ cropFrameTop: newTop })
  },

  onCropTouchEnd() {},

  confirmCrop() {
    wx.showLoading({ title: '处理中...' })
    const ctx = wx.createCanvasContext('cropCanvas')
    const screenWidth = wx.getSystemInfoSync().windowWidth
    const displayHeight = this.data.imageHeight && this.data.imageWidth
      ? (this.data.imageHeight / this.data.imageWidth) * screenWidth
      : screenWidth
    const scale = this.data.imageWidth / screenWidth
    const cropY = Math.round(this.data.cropFrameTop * scale)
    const cropH = Math.round(this.data.cropFrameHeight * scale)

    this.setData({ canvasWidth: screenWidth, canvasHeight: this.data.cropFrameHeight })

    setTimeout(() => {
      ctx.drawImage(this.data.cropImagePath, 0, cropY, this.data.imageWidth, cropH, 0, 0, screenWidth, this.data.cropFrameHeight)
      ctx.draw(false, () => {
        wx.canvasToTempFilePath({
          canvasId: 'cropCanvas',
          x: 0, y: 0,
          width: screenWidth, height: this.data.cropFrameHeight,
          destWidth: screenWidth, destHeight: this.data.cropFrameHeight,
          fileType: 'jpg', quality: 0.9,
          success: (res) => {
            wx.hideLoading()
            this.setData({ coverImage: res.tempFilePath, showCropper: false })
          },
          fail: () => {
            wx.hideLoading()
            this.setData({ coverImage: this.data.cropImagePath, showCropper: false })
            wx.showToast({ title: '裁切失败，使用原图', icon: 'none' })
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
        if (res.confirm) this.setData({ coverImage: '' })
      }
    })
  },

  preventTouch(e) {}
})
