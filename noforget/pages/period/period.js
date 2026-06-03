// pages/period/period.js — 姨妈追踪主页（云同步版）
const period = require('../../utils/period.js')
const {getIconPath} = require('../../utils/icons.js')
const countdownStore = require('../../utils/countdownStore.js')
const periodCloud = require('../../utils/periodCloud.js')
const SubscribeHelper = require('../../utils/subscribe-helper.js')

const app = getApp()

Page({
  data: {
    statusBarHeight: 20,
    navBarHeight: 44,
    totalTopHeight: 64,

    // 状态舱
    statusInfo: {hasData: false, mainLabel: '', subLabel: '', daysInfo: null, slogan: '', progress: null, phase: {}},
    prediction: null,

    // 月历
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    weekdays: ['一', '二', '三', '四', '五', '六', '日'],
    calendarCells: [],

    // 模态状态
    showPeriodModal: false,
    showLogModalFlag: false,
    periodDate: '',
    periodEndDate: '',

    // 统一底部弹窗
    showSheet: false,
    sheetType: '',
    sheetTitle: '',
    currentOptions: [],
    logDate: '',
    flowLabel: '',
    painLabel: '',
    symptomsLabel: '',
    moodLabel: '',

    // 姨妈来了状态开关
    isPeriodDay: false,

    // 记录表单
    logData: {
      flowLevel: 'none',
      painLevel: 'none',
      symptoms: [],
      mood: 'normal',
      notes: ''
    },

    // 选项字典
    dictFlow: [
      {key: 'none', label: '无'},
      {key: 'light', label: '少'},
      {key: 'medium', label: '中'},
      {key: 'heavy', label: '多'}
    ],
    dictPain: [
      {key: 'none', label: '无'},
      {key: 'slight', label: '轻微'},
      {key: 'moderate', label: '中度'},
      {key: 'severe', label: '严重'}
    ],
    dictSymptoms: [
      {key: 'cramp', label: '腰酸'},
      {key: 'bloating', label: '腹胀'},
      {key: 'fatigue', label: '乏力'},
      {key: 'headache', label: '头疼'},
      {key: 'nausea', label: '恶心'}
    ],
    dictMood: [
      {key: 'normal', label: '正常'},
      {key: 'irritable', label: '烦躁'},
      {key: 'low', label: '低落'},
      {key: 'happy', label: '愉快'}
    ],

    // 云同步状态
    cloudStatus: 'init' // 'init' | 'syncing' | 'synced' | 'offline'
  },

  onLoad(options) {
    // 获取导航栏高度
    try {
      const windowInfo = wx.getWindowInfo()
      const menuButton = wx.getMenuButtonBoundingClientRect()
      const statusBarHeight = windowInfo.statusBarHeight || 20
      const navBarHeight = (menuButton.top - statusBarHeight) * 2 + menuButton.height
      this.setData({
        statusBarHeight,
        navBarHeight: Math.round(navBarHeight),
        totalTopHeight: Math.round(statusBarHeight + navBarHeight)
      })
    } catch(e) {}

    // 如果有 id 参数（从首页跳转），用传入的姨妈日 id
    if (options.id) {
      this.setData({periodItemId: options.id})
    }

    // 初始化云同步（免登录获取openid）
    this.bootstrapPage()
  },

  async bootstrapPage() {
    await this.initCloud()
    await this.refreshAll()
  },

  // ─── 云同步初始化 ────────────────────────────────
  async initCloud() {
    this.setData({cloudStatus: 'init'})

    // 1. 初始化openid
    await periodCloud.init()

    // 2. 检查是否需要从云端拉取数据（版本迁移）
    const migrated = await periodCloud.checkMigration()
    if (migrated) {
      this.refreshAll() // 重新渲染拉取到的数据
      wx.showToast({title: '已从云端恢复数据', icon: 'none', duration: 2000})
    }

    // 3. 探测云端可用性
    const status = periodCloud.getStatus()
    if (!status.hasIdentity) {
      this.setData({cloudStatus: 'offline'})
    } else {
      this.setData({cloudStatus: 'synced'})
    }
  },

  async ensurePeriodSeed() {
    const entries = period.getEntries()
    if (Array.isArray(entries) && entries.length > 0) {
      return false
    }

    try {
      const cloudData = await periodCloud.downloadFromCloud()
      if (cloudData && Array.isArray(cloudData.entries) && cloudData.entries.length > 0) {
        return true
      }
    } catch (e) {}

    const fallbackId = this.data.periodItemId || 'period-item'
    const items = countdownStore.readLocalItems ? countdownStore.readLocalItems() : []
    const periodItem = Array.isArray(items)
      ? items.find(item => item && item.id === fallbackId && item.categoryId === 'period')
        || items.find(item => item && item.categoryId === 'period')
      : null

    if (!periodItem || !periodItem.targetDate) {
      return false
    }

    const restore = period.addEntry({startDate: periodItem.targetDate})
    return !!(restore && restore.success)
  },

  // ─── 触发云端同步 ───────────────────────────────
  triggerSync() {
    const entries = period.getEntries()
    const daily = period.getDailyRecords()
    const settings = period.getSettings()
    this.setData({cloudStatus: 'syncing'})
    periodCloud.scheduleSync(entries, daily, settings)
    // 2秒后更新状态
    setTimeout(() => {
      const st = periodCloud.getStatus()
      this.setData({cloudStatus: st.hasIdentity ? 'synced' : 'offline'})
    }, 2500)
  },

  // ─── 强制云端拉取 ───────────────────────────────
  async pullFromCloud() {
    wx.showLoading({title: '同步中...', mask: true})
    const data = await periodCloud.downloadFromCloud()
    wx.hideLoading()
    if (data) {
      this.refreshAll()
      wx.showToast({title: '已从云端同步', icon: 'success'})
    } else {
      wx.showToast({title: '云端无数据', icon: 'none'})
    }
  },

  /**
   * ✅ P1#8 修复：onShow 添加防抖保护
   * 每次页面切换都刷新全部数据会导致不必要的云同步和重渲染
   * 使用最后刷新时间戳，5秒内不重复刷新
   */
  _lastRefreshMs: 0,

  onShow() {
    const now = Date.now()
    if (now - (this._lastRefreshMs || 0) < 5000) return
    this._lastRefreshMs = now
    this.refreshAll()
  },

  async refreshAll() {
    const restored = await this.ensurePeriodSeed()
    const settings = period.getSettings()
    const entries = period.getEntries()
    const prediction = period.predictNext(entries, settings)

    const today = new Date()
    const year = this.data.currentYear || today.getFullYear()
    const month = this.data.currentMonth || today.getMonth() + 1
    const calendar = period.generateMonthCalendar(year, month, entries, prediction, settings.mode)
    const statusInfo = period.getStatusCardInfo(entries, prediction)
    const summaryCards = prediction ? [
      {
        key: 'next',
        iconPath: '/static/icons/system/moon-drop.svg',
        tone: 'rose',
        titleCn: '下次姨妈',
        titleEn: 'Next',
        value: period.formatMonthDay(prediction.predictedDate)
      },
      {
        key: 'peak',
        iconPath: '/static/icons/system/spark.svg',
        tone: 'blue',
        titleCn: '状态高点',
        titleEn: 'Peak',
        value: period.formatMonthDay(prediction.ovulationDate)
      },
      {
        key: 'focus',
        iconPath: '/static/icons/system/marker.svg',
        tone: 'gold',
        titleCn: '重点阶段',
        titleEn: 'Window',
        value: prediction.fertileWindow && prediction.fertileWindow.length >= 2
          ? `${period.formatMonthDay(prediction.fertileWindow[0])} - ${period.formatMonthDay(prediction.fertileWindow[1])}`
          : '—'
      }
    ] : []
    const phaseLegend = [
      {key: 'menstruate', label: '姨妈期', color: '#F5DCE8'},
      {key: 'follicular', label: '回升期', color: '#E3F1E1'},
      {key: 'ovulation', label: '状态高点', color: '#DCEAFE'},
      {key: 'fertile', label: '重点阶段', color: '#F7EFCF'}
    ]

    this.setData({
      calendarCells: calendar.cells,
      currentYear: year,
      currentMonth: month,
      prediction,
      statusInfo,
      settings,
      summaryCards,
      phaseLegend,
      isPeriodDay: statusInfo.phase?.key === 'menstruate'
    })

    if (restored) {
      this.triggerSync()
    }
  },

  // ─── 姨妈结束弹层逻辑 ───────────────────────────────
  showPeriodEndModal() {
    wx.vibrateShort({type: 'light'})
    const today = new Date().toISOString().split('T')[0]
    this.setData({showPeriodEndModal: true, periodEndDate: today})
  },
  hidePeriodEndModal() {
    this.setData({showPeriodEndModal: false, periodEndDate: ''})
  },
  onPeriodEndDateChange(e) {
    this.setData({periodEndDate: e.detail.value})
  },
  savePeriodEnd() {
    if (this._savingPeriodEnd) return
    if (!this.data.periodEndDate) {
      wx.showToast({title: '请选择日期', icon: 'none'})
      return
    }
    const entries = period.getEntries()
    if (!entries || entries.length === 0) {
      wx.showToast({title: '暂无开始记录', icon: 'none'})
      return
    }
    this._savingPeriodEnd = true
    const updated = period.updateEntryEndDate(entries[0].id, this.data.periodEndDate)
    if (updated) {
      wx.showToast({title: '已记录结束日', icon: 'success'})
      this.hidePeriodEndModal()
      this.refreshAll()
      this.triggerSync && this.triggerSync()
    } else {
      wx.showToast({title: '记录失败', icon: 'none'})
    }
    this._savingPeriodEnd = false
  },


  // ─── 导航 ───────────────────────────────────────
  goBack() {
    const pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.reLaunch({url: '/pages/index/index'})
    }
  },
  goSettings() {
    wx.navigateTo({url: '/pages/period/settings'})
  },
  async deleteCurrentPeriod() {
    const entries = period.getEntries()
    if (!entries || entries.length === 0) {
      wx.showToast({title: '暂无记录', icon: 'none'})
      return
    }
    wx.showModal({
      title: '删除确认',
      content: '确定要删除最近一条姨妈记录吗？删除后不可恢复。',
      confirmColor: '#B87888',
      cancelColor: '#9C8C82',
      success: async (res) => {
        if (res.confirm) {
          wx.vibrateShort({type: 'heavy'})
          const removed = period.removeEntry(entries[0].id)
          if (removed) {
            // 同步清理 countdownStore 中的 period item，防止首页幽灵卡片
            try {
              const allItems = await countdownStore.getItems() || []
              const periodItem = allItems.find(i => i.categoryId === 'period')
              if (periodItem) await countdownStore.removeItem(periodItem.id)
            } catch(e) { console.warn('[period] countdownStore cleanup failed', e) }
            wx.showToast({title: '已删除', icon: 'success'})
            this.refreshAll()
          } else {
            wx.showToast({title: '删除失败', icon: 'none'})
          }
        }
      }
    })
  },

  goStats() {
    wx.navigateTo({url: '/pages/period/stats'})
  },

  // ─── 月历 ───────────────────────────────────────
  prevMonth() {
    wx.vibrateShort({type: 'light'})
    let {currentYear, currentMonth} = this.data
    if (currentMonth === 1) {
      currentMonth = 12; currentYear -= 1
    } else {
      currentMonth -= 1
    }
    this.setData({currentYear, currentMonth})
    this.refreshCalendar()
  },
  nextMonth() {
    wx.vibrateShort({type: 'light'})
    let {currentYear, currentMonth} = this.data
    if (currentMonth === 12) {
      currentMonth = 1; currentYear += 1
    } else {
      currentMonth += 1
    }
    this.setData({currentYear, currentMonth})
    this.refreshCalendar()
  },
  refreshCalendar() {
    const settings = period.getSettings()
    const entries = period.getEntries()
    const prediction = period.predictNext(entries, settings)
    const calendar = period.generateMonthCalendar(
      this.data.currentYear, this.data.currentMonth,
      entries, prediction, settings.mode
    )
    this.setData({calendarCells: calendar.cells})
  },

  onDateTap(e) {
    const {date} = e.currentTarget.dataset
    if (!date) return
    this.setData({periodDate: date, showPeriodModal: true})
  },

  // ─── 周期记录弹层 ───────────────────────────────
  showPeriodStartModal() {
    wx.vibrateShort({type: 'light'})
    const today = new Date().toISOString().split('T')[0]
    this.setData({showPeriodModal: true, periodDate: today})
  },
  hidePeriodModal() {
    wx.vibrateShort({type: 'light'})
    this.setData({showPeriodModal: false, periodDate: '', periodEndDate: ''})
  },
  stopPropagation() {},

  onPeriodDateChange(e) {
    wx.vibrateShort({type: 'light'})
    this.setData({periodDate: e.detail.value})
  },

  async savePeriodStart() {
    if (this._savingPeriodStart) return
    if (!this.data.periodDate) {
      wx.showToast({title: '请选择日期', icon: 'none'})
      return
    }
    // 拦截未来日期
    const today = new Date().toISOString().split('T')[0]
    if (this.data.periodDate > today) {
      wx.showToast({title: '不能记录未来的日期', icon: 'none'})
      return
    }
    this._savingPeriodStart = true
    try {
      const result = period.addEntry({startDate: this.data.periodDate})
      if (result.success) {
        wx.showToast({title: '已记录，开始追踪', icon: 'success'})
        // 同步到 countdownStore，让首页卡片能显示
        try {
          const saveRes = await countdownStore.saveItem({
            id: 'period-item',
            title: '姨妈追踪',
            targetDate: this.data.periodDate,
            categoryId: 'period',
            isPeriod: true,
            createdAt: Date.now()
          })
          console.log('[period] countdownStore savePeriodStart:', saveRes)
        } catch(e) { console.warn('[period] countdownStore sync failed', e) }
        this.hidePeriodModal()
        this.refreshAll()
        // 云端增量同步
        this.triggerSync()
        // 订阅消息授权引导（记录成功后触发）
        SubscribeHelper.requestAuth()
      } else {
        wx.showToast({title: '该日期已记录', icon: 'none'})
      }
    } finally {
      this._savingPeriodStart = false
    }
  },

  // ─── 统一底部弹窗 ──────────────────────────────────
  showLogModal() {
    const today = new Date().toISOString().split('T')[0]
    const daily = period.getDailyRecords()
    const todayLog = daily[today] || {}
    const labels = this._computeLabels({
      flowLevel: todayLog.flowLevel || 'none',
      painLevel: todayLog.painLevel || 'none',
      symptoms: todayLog.symptoms || [],
      mood: todayLog.mood || 'normal',
      notes: todayLog.notes || ''
    })
    this.setData({
      showSheet: true,
      logDate: today,
      logData: {
        flowLevel: todayLog.flowLevel || 'none',
        painLevel: todayLog.painLevel || 'none',
        symptoms: todayLog.symptoms || [],
        mood: todayLog.mood || 'normal',
        notes: todayLog.notes || ''
      },
      ...labels,
      sheetType: '',
      sheetTitle: '',
      currentOptions: []
    })
  },

  openSheet(e) {
    const type = e.currentTarget.dataset.type
    const {logData} = this.data
    let title = '', options = [], selectedKeys = []

    if (type === 'flow') {
      title = '记录流量'
      options = this.data.dictFlow
      selectedKeys = [logData.flowLevel]
    } else if (type === 'pain') {
      title = '记录痛经'
      options = this.data.dictPain
      selectedKeys = [logData.painLevel]
    } else if (type === 'symptoms') {
      title = '记录症状（可多选）'
      options = this.data.dictSymptoms
      selectedKeys = logData.symptoms || []
    } else if (type === 'mood') {
      title = '记录情绪'
      options = this.data.dictMood
      selectedKeys = [logData.mood]
    }

    const renderOptions = options.map(item => ({
      ...item,
      selected: selectedKeys.includes(item.key)
    }))

    wx.vibrateShort({type: 'medium'})

    this.setData({
      sheetType: type,
      sheetTitle: title,
      currentOptions: renderOptions
    })
  },

  togglePeriodStatus() {
    const current = this.data.isPeriodDay
    this.setData({isPeriodDay: !current})
    wx.vibrateShort({type: 'heavy'})
    if (!current) {
      setTimeout(() => {
        this.openSheet({currentTarget: {dataset: {type: 'flow'}}})
      }, 300)
    }
  },

  handleOptionSelect(e) {
    const key = e.currentTarget.dataset.key
    const {sheetType, logData, currentOptions} = this.data
    const newLogData = {...logData}
    let newOptions = [...currentOptions]

    wx.vibrateShort({type: 'light'})

    if (sheetType === 'symptoms') {
      const sym = [...(newLogData.symptoms || [])]
      const idx = sym.indexOf(key)
      if (idx > -1) sym.splice(idx, 1)
      else sym.push(key)
      newLogData.symptoms = sym
      newOptions.forEach(opt => opt.selected = sym.includes(opt.key))
    } else {
      if (sheetType === 'flow') newLogData.flowLevel = key
      if (sheetType === 'pain') newLogData.painLevel = key
      if (sheetType === 'mood') newLogData.mood = key
      newOptions.forEach(opt => opt.selected = opt.key === key)
    }

    const labels = this._computeLabels(newLogData)
    this.setData({logData: newLogData, currentOptions: newOptions, ...labels})
  },

  closeSheetOptions() {
    this.setData({sheetType: '', sheetTitle: '', currentOptions: []})
  },

  closeSheet() {
    const {logDate, logData} = this.data
    if (logDate) {
      period.saveDailyRecord(logDate, {
        flowLevel: logData.flowLevel,
        painLevel: logData.painLevel,
        symptoms: logData.symptoms,
        mood: logData.mood,
        notes: logData.notes
      })
      this.triggerSync()
    }
    this.setData({showSheet: false, sheetType: '', sheetTitle: '', currentOptions: []})
  },

  onLogDateChange(e) {
    this.setData({logDate: e.detail.value})
  },

  stopPropagation() {},

  setNotes(e) {
    this.setData({'logData.notes': e.detail.value})
  },

  // 计算四个 label 辅助函数
  _computeLabels(logData) {
    const {dictFlow, dictPain, dictSymptoms, dictMood} = this.data
    const flowItem = dictFlow.find(i => i.key === logData.flowLevel)
    const painItem = dictPain.find(i => i.key === logData.painLevel)
    const moodItem = dictMood.find(i => i.key === logData.mood)
    const symptomLabels = (logData.symptoms || [])
      .map(k => dictSymptoms.find(i => i.key === k)?.label)
      .filter(Boolean)
    return {
      flowLabel: flowItem?.label || '',
      painLabel: painItem?.label || '',
      symptomsLabel: symptomLabels.length ? symptomLabels.join('、') : '',
      moodLabel: moodItem?.label || ''
    }
  },

  saveLog() {
    // 保留旧方法兼容性，内部委托给 closeSheet
    this.closeSheet()
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