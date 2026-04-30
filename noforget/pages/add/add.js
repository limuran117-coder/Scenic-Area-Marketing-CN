// pages/add/add.js - 添加/编辑页面逻辑
const app = getApp()
const countdown = require('../../utils/countdown.js')
const categories = require('../../utils/categories.js')

Page({
  data: {
    statusBarHeight: 20,
    title: '',
    targetDate: '',
    selectedCategory: 'birthday',
    direction: 'countdown',
    remindDays: 1,
    categories: categories.getAllCategories(),
    theme: {},
    currentTheme: 'apple',
    isEdit: false,
    editId: null,
    previewDays: 0,
    previewIsPast: false,
    previewIcon: '🎂',
    coverImage: '',
    // 裁切相关
    showCropper: false,
    cropImagePath: '',
    cropFrameTop: 0,
    cropFrameHeight: 240,
    imageHeight: 0,
    imageWidth: 0,
    touchStartY: 0,
    frameStartY: 0
  },

  onLoad(options) {
    const systemInfo = wx.getSystemInfoSync()
    const currentTheme = wx.getStorageSync('currentTheme') || 'apple'
    
    this.setData({
      statusBarHeight: systemInfo.statusInfo ? systemInfo.statusBarHeight : 20,
      currentTheme,
      theme: app.globalData.themes[currentTheme]
    })

    if (options.id) {
      this.setData({
        isEdit: true,
        editId: options.id
      })
      this.loadItem(options.id)
    } else {
      const cat = categories.getCategoryById('birthday')
      this.setData({
        direction: cat.direction,
        selectedCategory: 'birthday'
      })
    }
  },

  loadItem(id) {
    const items = wx.getStorageSync('countdownItems') || []
    const item = items.find(i => i.id === id)
    if (item) {
      const cat = categories.getCategoryById(item.categoryId)
      this.setData({
        title: item.title,
        targetDate: item.targetDate.split(' ')[0],
        selectedCategory: item.categoryId,
        direction: item.direction,
        remindDays: item.remindDays || 1,
        coverImage: item.coverImage || ''
      })
      this.updatePreview()
    }
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
    const cat = categories.getCategoryById(catId)
    this.setData({
      selectedCategory: catId,
      direction: cat.direction
    })
    this.updatePreview()
  },

  setDirection(e) {
    this.setData({ direction: e.currentTarget.dataset.dir })
    this.updatePreview()
  },

  setRemind(e) {
    this.setData({ remindDays: parseInt(e.currentTarget.dataset.days) })
  },

  updatePreview() {
    if (!this.data.targetDate) return
    const now = new Date()
    const diff = countdown.getExactDiff(new Date(this.data.targetDate), now)
    const cat = categories.getCategoryById(this.data.selectedCategory)
    this.setData({
      previewDays: diff.totalDays,
      previewIsPast: diff.isPast,
      previewIcon: cat.icon
    })
  },

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
    
    const newItem = {
      id: this.data.isEdit ? this.data.editId : Date.now().toString(),
      title: this.data.title.trim(),
      targetDate: this.data.targetDate,
      categoryId: this.data.selectedCategory,
      direction: this.data.direction,
      remindDays: this.data.remindDays,
      icon: cat.icon,
      coverImage: this.data.coverImage,
      createdAt: this.data.isEdit ? items.find(i => i.id === this.data.editId)?.createdAt : Date.now(),
      updatedAt: Date.now()
    }

    if (this.data.isEdit) {
      const index = items.findIndex(i => i.id === this.data.editId)
      if (index > -1) items[index] = newItem
    } else {
      items.push(newItem)
    }

    wx.setStorageSync('countdownItems', items)

    if (this.data.remindDays >= 0) {
      this.requestRemindPermission(newItem)
    }

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

  // 选择封面图片
  pickCoverImage() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        // 获取图片原始尺寸
        wx.getImageInfo({
          src: tempFilePath,
          success: (info) => {
            const screenWidth = wx.getSystemInfoSync().windowWidth
            const displayHeight = (info.height / info.width) * screenWidth
            // 裁切框高度 240px，初始居中
            const maxTop = Math.max(0, displayHeight - this.data.cropFrameHeight)
            this.setData({
              showCropper: true,
              cropImagePath: tempFilePath,
              imageWidth: info.width,
              imageHeight: info.height,
              cropFrameTop: maxTop / 2  //居中
            })
          },
          fail: () => {
            // 降级：直接使用
            this.setData({
              showCropper: true,
              cropImagePath: tempFilePath,
              cropFrameTop: 0
            })
          }
        })
      }
    })
  },

  // 取消裁切
  cancelCrop() {
    this.setData({
      showCropper: false,
      cropImagePath: '',
      cropFrameTop: 0
    })
  },

  // 开始拖动
  onCropTouchStart(e) {
    this.setData({
      touchStartY: e.touches[0].clientY,
      frameStartY: this.data.cropFrameTop
    })
  },

  // 拖动中
  onCropTouchMove(e) {
    const touchY = e.touches[0].clientY
    const delta = touchY - this.data.touchStartY
    const screenWidth = wx.getSystemInfoSync().windowWidth
    // 估算图片在屏幕上的显示高度
    const displayHeight = this.data.imageHeight && this.data.imageWidth
      ? (this.data.imageHeight / this.data.imageWidth) * screenWidth
      : screenWidth * 1.5
    const maxTop = Math.max(0, displayHeight - this.data.cropFrameHeight)
    let newTop = this.data.frameStartY + delta
    // 边界限制
    newTop = Math.max(0, Math.min(maxTop, newTop))
    this.setData({ cropFrameTop: newTop })
  },

  // 拖动结束
  onCropTouchEnd() {
    // nothing
  },

  // 确认裁切
  confirmCrop() {
    wx.showLoading({ title: '处理中...' })
    const ctx = wx.createCanvasContext('cropCanvas')
    const screenWidth = wx.getSystemInfoSync().windowWidth

    // 计算实际裁切区域
    const displayHeight = this.data.imageHeight && this.data.imageWidth
      ? (this.data.imageHeight / this.data.imageWidth) * screenWidth
      : screenWidth
    const scale = this.data.imageWidth / screenWidth
    const cropY = Math.round(this.data.cropFrameTop * scale)
    const cropH = Math.round(this.data.cropFrameHeight * scale)

    this.setData({
      canvasWidth: screenWidth,
      canvasHeight: this.data.cropFrameHeight
    })

    setTimeout(() => {
      ctx.drawImage(this.data.cropImagePath, 0, cropY, this.data.imageWidth, cropH, 0, 0, screenWidth, this.data.cropFrameHeight)
      ctx.draw(false, () => {
        wx.canvasToTempFilePath({
          canvasId: 'cropCanvas',
          x: 0,
          y: 0,
          width: screenWidth,
          height: this.data.cropFrameHeight,
          destWidth: screenWidth,
          destHeight: this.data.cropFrameHeight,
          fileType: 'jpg',
          quality: 0.9,
          success: (res) => {
            wx.hideLoading()
            this.setData({
              coverImage: res.tempFilePath,
              showCropper: false
            })
          },
          fail: () => {
            wx.hideLoading()
            // 降级：直接用原图
            this.setData({
              coverImage: this.data.cropImagePath,
              showCropper: false
            })
            wx.showToast({ title: '裁切失败，使用原图', icon: 'none' })
          }
        })
      })
    }, 100)
  },

  // 移除封面图片
  removeCoverImage() {
    wx.showModal({
      title: '移除封面',
      content: '确定要移除封面照片吗？',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          this.setData({ coverImage: '' })
        }
      }
    })
  },

  preventTouch(e) {
    // 阻止裁切弹层背景滚动
  }
})
