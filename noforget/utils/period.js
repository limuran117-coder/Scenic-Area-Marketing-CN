// utils/period.js — 姨妈追踪核心预测算法 v1.0
// 基于国际标准 28 天周期 + 14 天暴躁期，V2.0 接入动态修正

const { parseDateSafe, daysBetween, addDays, formatDate, formatMonthDay } = require('./date-utils')

// ─── 阶段定义 ───────────────────────────────────────
const PHASES = {
  menstruate: {
    key: 'menstruate',
    label: '姨妈',
    color: '#6A5572',
    bg: '#F5DCE8',
    icon: '🌸',
    description: '注意保暖，多喝热水'
  },
  follicular: {
    key: 'follicular',
    label: '回升',
    color: '#6D8B6A',
    bg: '#E3F1E1',
    icon: '🌿',
    description: '状态渐佳，适合制定计划'
  },
  ovulation: {
    key: 'ovulation',
    label: '状态高点',
    color: '#5D769B',
    bg: '#DCEAFE',
    icon: '✨',
    description: '阶段性状态高点，适合放慢节奏感受自己'
  },
  fertile: {
    key: 'fertile',
    label: '重点阶段',
    color: '#A88D52',
    bg: '#F7EFCF',
    icon: '🌱',
    description: '身体节奏更敏感的阶段，建议多留意状态'
  },
  luteal: {
    key: 'luteal',
    label: '暴躁',
    color: '#7B8FAA',
    bg: '#E4EDF8',
    icon: '🍂',
    description: '多休息，减少剧烈运动'
  },
  premenstrual: {
    key: 'premenstrual',
    label: '下次预警',
    color: '#A17B93',
    bg: '#F3E2EB',
    icon: '⏳',
    description: '姨妈即将来访'
  }
}

// ─── 本地存储 Key ────────────────────────────────────
const STORAGE_KEYS = {
  entries: 'periodEntries', // 姨妈记录数组 [PeriodEntry]
  daily: 'periodDaily', // 每日记录 { date: DailyRecord }
  settings: 'periodSettings' // 用户设置 PeriodSettings
}

// ─── 默认设置 ────────────────────────────────────────
const DEFAULT_SETTINGS = {
  cycleLength: 28,
  periodLength: 5,
  lutealPhase: 14,
  remindBefore: 3,
  remindEnabled: true,
  remindOnDay: true,
  pinEnabled: false,
  pinCode: '',
  mode: 'normal' // 'normal' | 'caution'
}

// ─── 核心算法 ────────────────────────────────────────

/**
 * 获取用户设置
 */
function getSettings() {
  try {
    const raw = wx.getStorageSync(STORAGE_KEYS.settings)
    return raw ? {...DEFAULT_SETTINGS, ...raw} : {...DEFAULT_SETTINGS}
  } catch(e) {
    return {...DEFAULT_SETTINGS}
  }
}

/**
 * 保存用户设置
 */
function saveSettings(settings) {
  wx.setStorageSync(STORAGE_KEYS.settings, settings)
}

/**
 * 获取所有姨妈记录（按开始日期倒序）
 */
function getEntries() {
  try {
    const raw = wx.getStorageSync(STORAGE_KEYS.entries)
    if (!raw) return []
    const entries = typeof raw === 'string' ? JSON.parse(raw) : raw
    return entries.sort((a, b) => parseDateSafe(b.startDate) - parseDateSafe(a.startDate))
  } catch(e) {
    return []
  }
}

/**
 * 保存姨妈记录
 */
function saveEntries(entries) {
  try {
    wx.setStorageSync(STORAGE_KEYS.entries, entries)
  } catch (e) {
    console.error('[period] saveEntries failed:', e)
  }
}

/**
 * 添加一条姨妈记录
 */
function addEntry(entry) {
  const entries = getEntries()
  // 检查是否与已有记录重叠
  const exists = entries.find(e => e.startDate === entry.startDate)
  if (exists) return {success: false, reason: 'duplicate', entry: exists}

  entries.unshift({
    id: Date.now().toString(),
    ...entry,
    cycleLength: entry.cycleLength || null,
    periodLength: entry.endDate
      ? daysBetween(entry.startDate, entry.endDate) + 1
      : (entry.periodLength || null),
    createdAt: Date.now()
  })
  recomputeEntryMetrics(entries)
  saveEntries(entries)
  return {success: true, entry: entries[0]}
}

/**
 * 更新姨妈结束日
 */
function updateEntryEndDate(entryId, endDate) {
  const entries = getEntries()
  const idx = entries.findIndex(e => e.id === entryId)
  if (idx === -1) return false
  entries[idx].endDate = endDate
  entries[idx].periodLength = daysBetween(entries[idx].startDate, endDate) + 1
  recomputeEntryMetrics(entries)
  saveEntries(entries)
  return true
}

/**
 * 获取每日记录
 */
function getDailyRecords() {
  try {
    const raw = wx.getStorageSync(STORAGE_KEYS.daily)
    return raw || {}
  } catch(e) {
    return {}
  }
}

/**
 * 保存每日记录
 */
function saveDailyRecord(date, record) {
  const daily = getDailyRecords()
  daily[date] = {...daily[date], ...record, date, loggedAt: Date.now()}
  wx.setStorageSync(STORAGE_KEYS.daily, daily)
}

/**
 * 预测下次姨妈开始日
 * @param {Array} entries 姨妈记录数组
 * @param {Object} settings 用户设置
 * @returns {Object} { predictedDate, ovulationDate, fertileWindow, safeStart }
 */
function predictNext(entries, settings) {
  const {cycleLength, lutealPhase, mode = 'normal'} = settings
  if (!entries || entries.length === 0) {
    return null
  }

  const normalizedEntries = normalizeEntries(entries)
  const intervalData = getCycleIntervals(normalizedEntries)

  if (intervalData.length === 0) {
    // 没有完整周期，用默认周期推算
    const lastStart = normalizedEntries[0].startDate
    const predictedDate = addDays(lastStart, cycleLength)
    const ovulationDate = addDays(lastStart, cycleLength - lutealPhase)
    const fertileWindow = buildFertileWindow(ovulationDate, mode)
    return {
      predictedDate,
      ovulationDate,
      fertileWindow,
      safeStart: addDays(ovulationDate, 4),
      cycleUsed: cycleLength,
      variability: null,
      confidence: 0.25,
      source: 'default'
    }
  }

  const recentCycles = intervalData.slice(0, Math.min(6, intervalData.length))
  let avgCycle = recentCycles.reduce((sum, item) => sum + item.length, 0) / recentCycles.length

  // V2.1 趋势修正（3个周期后启用）
  // ✅ P2#21 修复：clamp 趋势贡献在 ±7 天内，防止因单次异常偏移大量抖动
  if (recentCycles.length >= 3) {
    const rawTrend = recentCycles[0].length - recentCycles[1].length
    const clampedTrend = Math.min(7, Math.max(-7, rawTrend))
    avgCycle = avgCycle + (clampedTrend / recentCycles.length)
  }

  avgCycle = Math.round(avgCycle)
  avgCycle = Math.max(21, Math.min(35, avgCycle)) // 限制在21-35天

  const lastStart = normalizedEntries[0].startDate
  const predictedDate = addDays(lastStart, avgCycle)
  const ovulationDate = addDays(predictedDate, -lutealPhase)
  const fertileWindow = buildFertileWindow(ovulationDate, mode)

  // 安全期：危险日后4天开始
  const safeStart = addDays(ovulationDate, 4)
  const lengths = recentCycles.map(item => item.length)
  const minCycle = Math.min(...lengths)
  const maxCycle = Math.max(...lengths)
  const variability = maxCycle - minCycle
  const baseConfidence = recentCycles.length >= 6 ? 0.88 : recentCycles.length >= 3 ? 0.7 : 0.45
  const variabilityPenalty = Math.min(0.22, variability * 0.02)

  return {
    predictedDate,
    ovulationDate,
    fertileWindow,
    safeStart,
    avgCycle,
    cycleUsed: avgCycle,
    variability,
    source: recentCycles.length >= 3 ? 'adjusted' : 'average',
    confidence: Math.max(0.2, Math.min(0.95, Number((baseConfidence - variabilityPenalty).toFixed(2))))
  }
}

/**
 * 获取某日所处阶段
 * @param {string} date YYYY-MM-DD
 * @param {Array} entries 姨妈记录
 * @param {Object} prediction 预测结果
 * @param {string} mode 'normal' | 'trying' | 'prevent'
 */
function getPhaseForDate(date, entries, prediction, mode = 'normal') {
  const dateObj = parseDateSafe(date)
  const settings = getSettings()
  const defaultPeriodLength = settings.periodLength || 5
  const lutealPhase = settings.lutealPhase || 14

  // ★ 修复：内部排序，确保 entries[0] 是最新记录，防止调用方传乱序数据
  const sortedEntries = Array.isArray(entries)
    ? [...entries].sort((a, b) => parseDateSafe(b.startDate) - parseDateSafe(a.startDate))
    : []

  // 检查是否是姨妈第一天
  const periodStart = sortedEntries.find(e => e.startDate === date)
  if (periodStart) {
    return {...PHASES.menstruate, subLabel: '第1天'}
  }

  // 检查是否在姨妈期中
  if (sortedEntries.length > 0) {
    const lastStart = sortedEntries[0].startDate
    const lastEntry = sortedEntries[0]

    // P1-2修复：如果没有结束日期，用默认天数兜底但保留弹性窗口
    // 如果无endDate且距今天<14天，按未结束处理（防止超过5天就自动截断）
    let periodEnd
    if (lastEntry.endDate) {
      periodEnd = parseDateSafe(lastEntry.endDate)
    } else {
      const daysSinceStart = daysBetween(lastStart, dateObj)
      const maxTolerant = Math.max(defaultPeriodLength - 1, 13) // 至少14天窗口
      periodEnd = addDays(lastStart, Math.min(daysSinceStart + 1, maxTolerant))
    }

    if (dateObj >= parseDateSafe(lastStart) && dateObj <= periodEnd) {
      const dayNum = daysBetween(lastStart, date) + 1
      return {...PHASES.menstruate, subLabel: `第${dayNum}天`}
    }

    // 姨妈结束后，使用 prediction 计算各阶段
    if (prediction) {
      const fertileStart = prediction.fertileWindow && prediction.fertileWindow[0]
        ? parseDateSafe(prediction.fertileWindow[0])
        : addDays(prediction.ovulationDate, -4)

      // 回升期：姨妈结束后（periodEnd）到危险日前4天
      if (dateObj > periodEnd && dateObj < fertileStart) {
        return {...PHASES.follicular}
      }

      // 危险期：排卵日前4天到前1天
      if (dateObj >= fertileStart && dateObj < prediction.ovulationDate) {
        return {...PHASES.fertile}
      }

      // 危险日
      if (formatDate(dateObj) === formatDate(prediction.ovulationDate)) {
        return {...PHASES.ovulation}
      }

      // 暴躁期：排卵日后到下次姨妈前
      if (dateObj > prediction.ovulationDate && dateObj < prediction.predictedDate) {
        const daysToPeriod = daysBetween(date, prediction.predictedDate)
        // 今天就是预测日 → 姨妈可能已来（0天不能用"下次预警"）
        if (daysToPeriod === 0) {
          return {...PHASES.menstruate, subLabel: '预计今天见姨妈'}
        }
        // 下次预警：距离下次预计 1~3 天
        if (daysToPeriod <= 3) {
          return {...PHASES.premenstrual, subLabel: `⏳ 姨妈${daysToPeriod}天后来访`}
        }
        if (mode === 'caution' && daysToPeriod <= lutealPhase) {
          return {...PHASES.luteal, subLabel: `暴躁期 · ${daysToPeriod}天后`}
        }
        return {...PHASES.luteal}
      }
    }
  }

  return {key: 'none', label: '', color: '', bg: '', icon: ''}
}

/**
 * 生成月历数据（某月所有日期的阶段标记）
 */
function generateMonthCalendar(year, month, entries, prediction, _mode) {
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  const startWeekday = firstDay.getDay() || 7 // 周一=1，周日=7
  const daysInMonth = lastDay.getDate()

  const cells = []

  // 填充上月空白格
  for (let i = 1; i < startWeekday; i++) {
    cells.push({day: null, empty: true})
  }

  // 当月日期
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const cellDate = parseDateSafe(dateStr)
    const cellTime = cellDate.getTime()
    const today = new Date()
    const isToday = formatDate(new Date(year, month - 1, d)) === formatDate(today)

    // ─── 精准四色阶段判断 ────────────────────────────────
    let phase = null

    // 1. 遍历所有历史记录，判断是否是姨妈期
    let latestPeriodEnd = 0
    entries.forEach(entry => {
      const startTs = parseDateSafe(entry.startDate).getTime()
      const endTs = entry.endDate
        ? parseDateSafe(entry.endDate).getTime()
        : startTs + 4 * 86400000 // 默认5天
      if (cellTime >= startTs && cellTime <= endTs) {
        phase = {key: 'menstruate', bg: '#D6BDE8', color: '#FFFFFF'}
      }
      if (endTs > latestPeriodEnd) latestPeriodEnd = endTs
    })

    // 2. 非姨妈期，用 prediction 推算其他三阶段
    if (!phase && prediction) {
      const ovulationTs = parseDateSafe(prediction.ovulationDate).getTime()
      const nextPeriodTs = parseDateSafe(prediction.predictedDate).getTime()
      const fertileStartTs = ovulationTs - 4 * 86400000
      const fertileEndTs = ovulationTs + 3 * 86400000

      if (cellTime === ovulationTs) {
        phase = {key: 'ovulation', bg: '#DCEAFE', color: '#4A3728'}
      } else if (cellTime >= fertileStartTs && cellTime < ovulationTs) {
        phase = {key: 'fertile', bg: '#F7EFCF', color: '#4A3728'}
      } else if (cellTime > fertileEndTs && cellTime < nextPeriodTs) {
        if (cellTime >= nextPeriodTs - 3 * 86400000) {
          phase = {key: 'premenstrual', bg: '#F3E2EB', color: '#4A3728'}
        } else {
          phase = {key: 'luteal', bg: '#E3F1E1', color: '#4A3728'}
        }
      } else if (cellTime > latestPeriodEnd && cellTime < fertileStartTs) {
        phase = {key: 'follicular', bg: '#E3F1E1', color: '#4A3728'}
      }
    }

    cells.push({
      day: d,
      date: dateStr,
      isToday,
      phase
    })
  }

  return {cells, year, month, daysInMonth}
}

/**
 * 获取顶部状态舱信息
 */
function getStatusCardInfo(entries, prediction) {
  // 防御：确保 entries 是有效数组
  if (!Array.isArray(entries)) entries = []
  // ★ 修复：内部排序确保 entries[0] 是最新记录
  const sortedEntries = [...entries].sort((a, b) => parseDateSafe(b.startDate) - parseDateSafe(a.startDate))
  if (!prediction || !prediction.predictedDate) {
    const has = sortedEntries.length > 0
    return {
      hasData: has,
      mainLabel: has ? '已记录开始日' : '开始记录你的姨妈',
      subLabel: has ? '正在为你生成预测' : '记录你的姨妈开始日，开始追踪',
      headlineNumber: has ? 1 : null,
      headlineUnit: '天',
      headlineHint: has ? '刚开始记录' : '等待记录',
      currentCycleDay: has ? 1 : null,
      daysInfo: null,
      phase: has ? PHASES.menstruate : {key: 'none', label: '', color: '', bg: '', icon: ''},
      progress: null,
      slogan: has ? '先把今天记下，剩下的交给时间' : '记录身体变化，也是在认真照顾自己'
    }
  }

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayStr = formatDate(today)
  const todayPhase = getPhaseForDate(todayStr, sortedEntries, prediction)

  const predictDate = parseDateSafe(prediction.predictedDate)
  predictDate.setHours(0, 0, 0, 0)
  const diffTime = predictDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (todayPhase.key === 'menstruate') {
    const lastStart = sortedEntries[0].startDate
    const dayInPeriod = daysBetween(lastStart, todayStr) + 1
    return {
      hasData: true,
      mainLabel: `第 ${dayInPeriod} 天`,
      subLabel: todayPhase.subLabel || '好好休息',
      headlineNumber: dayInPeriod,
      headlineUnit: '天',
      headlineHint: '当前阶段',
      currentCycleDay: dayInPeriod,
      daysInfo: null,
      phase: PHASES.menstruate,
      progress: Math.max(0, Math.min(100, Math.round((dayInPeriod / (sortedEntries[0].periodLength || 5)) * 100))),
      slogan: getSlogan('menstruate', dayInPeriod)
    }
  }

  let cycleDay = null
  if (sortedEntries.length > 0) {
    const lastStart = sortedEntries[0].startDate
    cycleDay = daysBetween(lastStart, todayStr) + 1
  }

  let mainLabel = ''
  let slogan = getSlogan(todayPhase.key || 'unknown', cycleDay || 0)

  // 🌟 核心修复：有符号天数，区分未来倒数 vs 过去推迟
  if (diffDays > 0) {
    mainLabel = `距姨妈还有 ${diffDays} 天`
  } else if (diffDays === 0) {
    mainLabel = '预计今天见姨妈'
    slogan = '注意保暖，别喝冰水哦'
  } else {
    mainLabel = `姨妈已推迟 ${Math.abs(diffDays)} 天`
    slogan = '放轻松，推迟几天也正常'
  }

  return {
    hasData: true,
    mainLabel,
    subLabel: todayPhase.label ? `${todayPhase.icon} ${todayPhase.label}` : '无记录',
    headlineNumber: Math.abs(diffDays),
    headlineUnit: '天',
    headlineHint: diffDays > 0 ? '距离下次' : diffDays === 0 ? '预计今日' : '已推迟',
    currentCycleDay: cycleDay,
    daysInfo: cycleDay !== null ? `第 ${cycleDay} 天` : null,
    phase: todayPhase,
    progress: prediction.avgCycle
      ? Math.min(100, Math.round((cycleDay || 0) / prediction.avgCycle * 100))
      : null,
    slogan
  }
}

/**
 * 情绪 Slogan 生成
 */
function getSlogan(phase, cycleDay) {
  const slogans = {
    menstruate: [
      '多喝温水，记得照顾好自己 🌸',
      '第二天，身体在慢慢恢复，多休息',
      '暖暖的，很舒服 💆‍♀️',
      '给自己一个放松的理由',
      '热敷小腹，给自己一个温暖的拥抱 🤗',
      '这几天对自己好点，甜品不设限 🍫',
      '身体在忙，早点睡美容觉 🌙',
      '第一天勇敢，第二天好好休息',
      '肚子凉凉的时候，一杯热红糖姜茶很治愈 ☕',
      '姨妈期是身体在和你说话，耐心听它说',
      '别逞强，重活留到下周期 🌿',
      '舒服的时候，可以轻轻伸展一下 🧘‍♀️',
      '保暖是这几天最重要的小事 🧣',
      '身体正在提醒你慢一点 💐',
      '这几天别太在意体重数字',
      '吃点温热好消化的，给肠胃放个假 🍲',
      '情绪起伏时，也要温柔对待自己',
      '前两天更要记得照顾好自己 🌼',
      '姨妈期不舒服来了也不怕，深呼吸缓解 ☁',
      '姨妈期最后两天，身体已经在悄悄恢复了'
    ],
    follicular: [
      '新周期开始了，感觉充满力量 ✨',
      '回升期到了，状态渐佳，适合冲刺 🚀',
      '心情明媚，计划起来吧 🌿',
      '身体在积蓄能量，好事将近 🌱',
      '雌激素回升，皮肤状态都在变好 💫',
      '这几天记忆力不错，适合学点新东西 📚',
      '回升期适合设定目标，然后一步步实现 🎯',
      '皮肤在发光，这几天素颜也好看 ✨',
      '身体感觉轻盈，很适合运动 💪',
      '新周期新气象，写下这个月的愿望清单 📝',
      '状态回来了，做事效率翻倍 ⚡',
      '精力充沛，可以安排一些挑战性任务 🌟',
      '回升期心情好，社交运也在上升 💕',
      '给自己买束花，犒赏认真的自己 🌸',
      '身体在发出积极信号，好状态会持续 🌈',
      '适合开始一个新的小习惯 🌱',
      '恢复期的皮肤吸收力好，做个保湿面膜 💆‍♀️',
      '代谢加快，身材线条也在变好 💃',
      '卵泡期是每个月状态最好的时段 🌞',
      '身心都在向上走，感受这份向上的力量 📈'
    ],
    ovulation: [
      '✨ 今天是状态高点，先照顾好自己',
      '状态高点里，心情愉悦很重要 💕',
      '最适合专注自己的日子 💎',
      '身体给你的礼物日，好好享受 🎁',
      '今天是本月状态最好的一天 ✨',
      '雌激素高峰，皮肤在发光 💫',
      '心情美美的，适合约闺蜜下午茶 ☕',
      '今天适合做一些重要决定 🌟',
      '身体正在巅峰，状态拉满 ⚡',
      '✨ 今天整个人都在发光',
      '最适合见喜欢的人，心情最美的时候 💗',
      '雌激素高峰期，记忆力情绪都在高位 🧠',
      '皮肤通透，这几天不用妆也好看 🌸',
      '今天适合表白或者推进重要关系 💌',
      '身体在告诉你，这几天值得被宠爱 👑',
      '活跃度高，社交运爆棚 🎉',
      '今天是高效日，处理重要事务事半功倍 💼',
      '皮肤状态好到发光，省下护肤品的钱 🛍',
      '心情愉悦，看什么都顺眼 🌈',
      '身体和情绪都在最佳状态，享受这天的美好 🌞'
    ],
    fertile: [
      '重点阶段到了，多留意自己的节奏 💚',
      '这几天更适合把节奏放慢一点 🌿',
      '身体给你的礼物日 🌱',
      '最适合专注自己的日子 💕',
      '重点阶段到了，这几天多留意 🌿',
      '这几天身体节奏会有变化，注意休息 🧘‍♀️',
      '如果觉得疲惫，先把照顾自己放在前面 🛡',
      '身体正在为可能的到来做准备 💫',
      '这期间情绪可能更敏感，多给自己空间 🌸',
      '重点阶段不代表焦虑，只是节奏变化更明显 🌾',
      '这几天更适合温和观察身体状态 🎯',
      '身体在发出信号，尊重它就好 🌱',
      '这几天情绪起伏一些也很常见 😊',
      '这期间皮肤可能会更敏感，用温和的护肤品 💧',
      '多摄入蛋白质，身体正在积极准备 🌿',
      '这几天体感有波动也很常见 🌡',
      '如果焦虑，记录下来，情绪需要出口 📝',
      '身体给你的最好状态，珍惜每一天 ✨',
      '状态好的时候，也别忘了给自己留白 💗',
      '尊重身体节律，每一天都值得认真对待 🌞'
    ],
    luteal: [
      '暴躁期多休息，别太累 🍂',
      '身体在准备，多吃温热食物 🍵',
      '给自己一个轻松的下午 🌿',
      '经前期身体在调整，多给自己耐心 🌸',
      '暴躁期到了，少想多做，多休息 🍂',
      '黄体期代谢变慢，少吃重口味 🌶',
      '经前期综合征来了，写下来然后放过自己 📝',
      '暴躁期情绪波动是正常的，不是你的错 💗',
      '身体在积蓄能量，为下个周期做准备 🌱',
      '多吃含镁的食物，缓解烦躁感 🥬',
      '暴躁期皮肤可能会变差，温和护肤就好 💆‍♀️',
      '身体在提醒你需要休息，尊重这个信号 🌙',
      '黄体期乳房胀痛是正常的，少喝咖啡可以缓解 ☕',
      '经前期想吃甜的，适量就好，别压抑自己 🍫',
      '暴躁期适合做轻度瑜伽，疏通肝气 🧘‍♀️',
      '身体正在说：慢一点，温柔一点 🌸',
      '黄体期体温偏高是正常的，别担心 🌡',
      '经前期的焦虑会过去，给自己一点耐心 ⏳',
      '暴躁期皮肤敏感，换用温和护肤品 💧',
      '身体在认真为下个周期做准备，好事即将发生 🌺'
    ],
    unknown: [
      '记录身体，感受变化 📝',
      '每一天都值得被记录 🌸',
      '认真对待自己，从每一天开始 💗',
      '身体是值得探索的小宇宙 🌏',
      '记录本身就是爱自己的方式 🌱',
      '每一天都有值得记录的美好 🌟',
      '给自己一个拥抱，感谢身体 🌸',
      '倾听身体的声音，它会告诉你答案 💫',
      '认真的记录，是对自己最温柔的照顾 💗',
      '身体是灵魂的家，好好爱它 🏠',
      '每个当下都是了解自己的好时机 🌸',
      '数据背后是你对自己认真的关注 📊',
      '记录让身体的变化可见，可贵 🌿',
      '好好记录，是变好的开始 ✨',
      '你的坚持，本身就是一种美好 💗',
      '身体每天都在说话，你听到了吗 🌸',
      '记录让生活更有掌控感 📝',
      '认真的女生最美丽 💫',
      '每个记录都是给自己的一封情书 💌',
      '爱自己，从认真记录每一天开始 🌸'
    ]
  }
  const pool = slogans[phase] || slogans.unknown
  // cycleDay 从 1 开始，数组从 0 开始，需要 -1 对齐
  return pool[(cycleDay - 1) % pool.length]
}

/**
 * 获取近3个月周期列表（用于统计页）
 */
function getRecentCycles(entries, limit = 3) {
  return getCycleIntervals(entries)
    .slice(0, limit)
    .map(item => ({
      start: item.start,
      end: item.end,
      length: item.length,
      stable: item.length >= 25 && item.length <= 32,
      periodLength: item.periodLength || null
    }))
}

/**
 * 计算间隔统计
 */
function getCycleStats(entries) {
  const intervals = getCycleIntervals(entries)
  if (intervals.length === 0) return null

  const lengths = intervals.map(item => item.length)
  const avg = lengths.reduce((a, b) => a + b, 0) / lengths.length
  const min = Math.min(...lengths)
  const max = Math.max(...lengths)
  const variability = max - min
  const confidence = Math.max(0.2, Math.min(0.95, (intervals.length >= 6 ? 0.88 : intervals.length >= 3 ? 0.7 : 0.45) - variability * 0.02))

  return {
    avgCycle: Math.round(avg * 10) / 10,
    minCycle: min,
    maxCycle: max,
    dataPoints: intervals.length,
    confidence: Math.round(confidence * 100),
    isStable: (max - min) <= 4 && min >= 21
  }
}

function normalizeEntries(entries) {
  if (!Array.isArray(entries)) return []
  const cloned = entries.map(entry => ({...entry}))
  recomputeEntryMetrics(cloned)
  return cloned.sort((a, b) => parseDateSafe(b.startDate) - parseDateSafe(a.startDate))
}

function recomputeEntryMetrics(entries) {
  if (!Array.isArray(entries)) return entries
  entries.sort((a, b) => parseDateSafe(b.startDate) - parseDateSafe(a.startDate))
  entries.forEach((entry, index) => {
    if (entry.endDate) {
      entry.periodLength = daysBetween(entry.startDate, entry.endDate) + 1
    } else if (!entry.periodLength) {
      entry.periodLength = null
    }

    const nextEntry = entries[index + 1]
    if (nextEntry && nextEntry.startDate) {
      entry.cycleLength = daysBetween(entry.startDate, nextEntry.startDate)
    } else if (!Number.isFinite(entry.cycleLength)) {
      entry.cycleLength = null
    }
  })
  return entries
}

function getCycleIntervals(entries) {
  const normalizedEntries = normalizeEntries(entries)
  const intervals = []
  for (let i = 0; i < normalizedEntries.length - 1; i++) {
    const current = normalizedEntries[i]
    const next = normalizedEntries[i + 1]
    const length = daysBetween(current.startDate, next.startDate)
    if (!Number.isFinite(length) || length <= 0) continue
    intervals.push({
      start: next.startDate,
      end: current.startDate,
      length,
      periodLength: current.periodLength || (current.endDate ? daysBetween(current.startDate, current.endDate) + 1 : null)
    })
  }
  return intervals
}

function buildFertileWindow(ovulationDate, mode = 'normal') {
  const startOffset = mode === 'caution' ? -5 : -4
  const endOffset = 3
  return [
    addDays(ovulationDate, startOffset),
    addDays(ovulationDate, endOffset)
  ]
}

// ─── 工具函数：已迁移至 utils/date-utils.js ──────────

/**
 * 删除一条姨妈记录
 * @param {string} entryId
 * @returns {boolean}
 */
function removeEntry(entryId) {
  const entries = getEntries()
  const idx = entries.findIndex(e => e.id === entryId)
  if (idx === -1) return false
  entries.splice(idx, 1)
  recomputeEntryMetrics(entries)
  saveEntries(entries)
  return true
}

module.exports = {
  STORAGE_KEYS,
  DEFAULT_SETTINGS,
  PHASES,
  getSettings,
  saveSettings,
  getEntries,
  saveEntries,
  addEntry,
  updateEntryEndDate,
  removeEntry,
  getDailyRecords,
  saveDailyRecord,
  predictNext,
  getPhaseForDate,
  generateMonthCalendar,
  getStatusCardInfo,
  getRecentCycles,
  getCycleStats,
  getSlogan,
  daysBetween,
  addDays,
  formatDate,
  formatMonthDay
}
