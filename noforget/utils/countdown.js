// utils/countdown.js - 倒计时/正向计时核心算法 v2
// 支持 isRecurring（年度循环）和 startDate（存活计时）

/**
 * 计算两个日期之间的差值（天为单位）
 * @param {Date|string} targetDate
 * @param {Date} nowDate
 * @returns {Object} { days, isPast, diffMs }
 */
function getDiff(targetDate, nowDate = new Date()) {
  const target = new Date(targetDate)
  const now = new Date(nowDate)

  // 重置到00:00:00只比较日期
  const targetDay = new Date(target.getFullYear(), target.getMonth(), target.getDate())
  const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  const diffMs = targetDay.getTime() - nowDay.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  return {
    days: Math.abs(diffDays),
    isPast: diffMs < 0,
    diffMs
  }
}

/**
 * 计算精确的年月日时分秒差值
 * @param {Date|string} targetDate
 * @param {Date} nowDate
 * @returns {Object}
 */
function getExactDiff(targetDate, nowDate = new Date()) {
  const target = new Date(targetDate)
  const now = new Date(nowDate)

  let years = target.getFullYear() - now.getFullYear()
  let months = target.getMonth() - now.getMonth()
  let days = target.getDate() - now.getDate()
  let hours = target.getHours() - now.getHours()
  let minutes = target.getMinutes() - now.getMinutes()
  let seconds = target.getSeconds() - now.getSeconds()

  // 规范化负值
  if (seconds < 0) { seconds += 60; minutes -= 1 }
  if (minutes < 0) { minutes += 60; hours -= 1 }
  if (hours < 0) { hours += 24; days -= 1 }
  if (days < 0) {
    const lastMonth = new Date(target.getFullYear(), target.getMonth(), 0)
    days += lastMonth.getDate()
    months -= 1
  }
  if (months < 0) { months += 12; years -= 1 }

  const isPast = target.getTime() < now.getTime()

  return {
    years: Math.abs(years),
    months: Math.abs(months),
    days: Math.abs(days),
    hours: Math.abs(hours),
    minutes: Math.abs(minutes),
    seconds: Math.abs(seconds),
    totalDays: Math.floor(Math.abs(target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)),
    isPast,
    rawDiff: target.getTime() - now.getTime()
  }
}

/**
 * ============================================================
 * 核心函数：计算"下一个目标日期"的主倒计时（用于大字显示）
 * ============================================================
 *
 * 逻辑：
 * - isRecurring=true：找到今年（若已过则明年）的"月.日"
 * - isRecurring=false：直接用 targetDate 作为终点
 *
 * @param {Object} item - { targetDate, isRecurring, direction }
 * @param {Date} now
 * @returns {Object} { days, hours, minutes, seconds, totalFormatted, isPast }
 */
function getMainCountdown(item, now = new Date()) {
  const target = new Date(item.targetDate)
  let endDate

  if (item.isRecurring) {
    // 年度循环：找今年或明年的同月同日
    endDate = new Date(now.getFullYear(), target.getMonth(), target.getDate())
    if (endDate <= now) {
      endDate = new Date(now.getFullYear() + 1, target.getMonth(), target.getDate())
    }
  } else {
    // 一次性倒计时：直接以目标日期为终点
    endDate = new Date(target.getFullYear(), target.getMonth(), target.getDate())
  }

  const diffMs = endDate.getTime() - now.getTime()
  const isPast = diffMs < 0
  const absMs = Math.abs(diffMs)

  const days  = Math.floor(absMs / (1000 * 60 * 60 * 24))
  const hours = Math.floor((absMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const mins  = Math.floor((absMs % (1000 * 60 * 60)) / (1000 * 60))
  const secs  = Math.floor((absMs % (1000 * 60)) / 1000)

  const totalFormatted = `${days}天 ${String(hours).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`

  return { days, hours, minutes: mins, seconds: secs, totalFormatted, isPast }
}

/**
 * ============================================================
 * 核心函数：计算"已存活/已过去"时间（用于小字显示）
 * ============================================================
 *
 * 逻辑：
 * - 有 startDate 且 isRecurring=true：计算 startDate → now 的年月日差
 *   → 例：1987-09-12 出生，现在2026-05-01 → "已过去 38 年 8 个月"
 * - 一次性事件（isRecurring=false）：返回 "已过 X 天" 或 "还有 X 天"
 *
 * @param {Object} item - { startDate, isRecurring, direction }
 * @param {Date} now
 * @returns {Object} { text, years, months, days, totalDays, isPast }
 */
function getElapsedText(item, now = new Date()) {
  const { startDate, isRecurring } = item

  if (startDate && isRecurring) {
    // 方式：从 startDate 到现在，计算自然年月差
    const start = new Date(startDate)
    let y = now.getFullYear() - start.getFullYear()
    let m = now.getMonth() - start.getMonth()
    let d = now.getDate() - start.getDate()

    if (d < 0) {
      m -= 1
      const prevMonth = new Date(now.getFullYear(), now.getMonth(), 0)
      d += prevMonth.getDate()
    }
    if (m < 0) { m += 12; y -= 1 }

    const totalDays = Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
    const isPast = true

    let text
    if (y >= 1) {
      text = `已过去 ${y} 年 ${m} 个月`
    } else if (m >= 1) {
      text = `已过去 ${m} 个月`
    } else {
      text = `已过去 ${totalDays} 天`
    }

    return { text, years: y, months: m, days: d, totalDays, isPast }
  } else {
    // 一次性倒计时
    const diff = getDiff(item.targetDate, now)
    const text = diff.isPast
      ? `已过 ${diff.days} 天`
      : `还有 ${diff.days} 天`
    return { text, years: 0, months: 0, days: diff.days, totalDays: diff.days, isPast: diff.isPast }
  }
}

/**
 * 格式化显示文本
 */
function formatDisplayText(diff, isCountUp = false) {
  if (diff.isPast || isCountUp) {
    if (diff.years > 0) {
      return `${diff.years}年${diff.months}个月${diff.days}天`
    } else if (diff.months > 0) {
      return `${diff.months}个月${diff.days}天`
    } else if (diff.days > 0) {
      return `${diff.days}天`
    } else {
      return `${diff.hours}小时`
    }
  } else {
    if (diff.years > 0) {
      return `${diff.years}年${diff.months}个月`
    } else if (diff.months > 0) {
      return `${diff.months}个月${diff.days}天`
    } else if (diff.days > 0) {
      return `${diff.days}天`
    } else if (diff.hours > 0) {
      return `${diff.hours}小时${diff.minutes}分钟`
    } else {
      return `${diff.minutes}分钟`
    }
  }
}

/**
 * 倒计时一句话描述（兼容旧接口）
 */
function getCountdownSentence(item, diff) {
  if (item.direction === 'countup') {
    const y = diff.years
    const m = diff.months
    if (y >= 1) {
      return `已过去 ${y} 年 ${m} 个月`
    } else if (m >= 1) {
      return `已过去 ${m} 个月`
    } else {
      return `已过去 ${diff.days} 天`
    }
  } else {
    return diff.isPast
      ? `已过 ${diff.totalDays} 天`
      : `还有 ${diff.totalDays} 天`
  }
}

/**
 * 精确倒计时（兼容旧接口，用于 getPreciseCountdown）
 */
function getPreciseCountdown(item, now = new Date()) {
  return getMainCountdown(item, now)
}

/**
 * 获取下一个里程碑
 */
function getNextMilestone(startDate, currentDays) {
  const milestones = [100, 200, 365, 500, 666, 1000, 1500, 2000, 3000, 3650, 5000, 10000]
  for (const milestone of milestones) {
    if (milestone > currentDays) {
      const targetDate = new Date(startDate)
      targetDate.setDate(targetDate.getDate() + milestone)
      const diff = getDiff(targetDate)
      return { milestone, daysLeft: diff.days, targetDate }
    }
  }
  return null
}

/**
 * 格式化数字（千分位）
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function isToday(date) {
  const d = new Date(date)
  const today = new Date()
  return d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
}

function isTomorrow(date) {
  const d = new Date(date)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return d.getDate() === tomorrow.getDate() &&
    d.getMonth() === tomorrow.getMonth() &&
    d.getFullYear() === tomorrow.getFullYear()
}

module.exports = {
  getDiff,
  getExactDiff,
  getMainCountdown,
  getElapsedText,
  formatDisplayText,
  formatNumber,
  getNextMilestone,
  isToday,
  isTomorrow,
  getCountdownSentence,
  getPreciseCountdown   // 兼容旧接口，透传到 getMainCountdown
}
