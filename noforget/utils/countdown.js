// utils/countdown.js - 倒计时/正向计时核心算法 v3
// 修复：iOS Date NaN 问题，统一使用 date-utils 模块

const { parseDateSafe } = require('./date-utils')

/**
 * 判断是否为闰年（2月29日检查用）
 */
function isLeapYear(year) {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0
}

/**
 * 计算两个日期之间的差值（天为单位）
 * @param {Date|string} targetDate
 * @param {Date} nowDate
 * @returns {Object} { days, isPast, diffMs }
 */
function getDiff(targetDate, nowDate = new Date()) {
  const target = parseDateSafe(targetDate)
  const now = parseDateSafe(nowDate)

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
  if (item && item.direction === 'countup') {
    const elapsed = getElapsedText(item, now)
    return {
      days: elapsed.totalDays || 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      totalFormatted: `${elapsed.totalDays || 0}天 00:00:00`,
      isPast: true
    }
  }

  const targetStr = item.targetDate
  // 防御：null/undefined/空字符串/invalid → 兜底返回0
  if (!targetStr || typeof targetStr !== 'string' || targetStr.trim() === '') {
    return {days: 0, hours: 0, minutes: 0, seconds: 0, totalFormatted: '0天 00:00:00', isPast: false}
  }
  const target = parseDateSafe(targetStr)
  if (isNaN(target.getTime())) {
    return {days: 0, hours: 0, minutes: 0, seconds: 0, totalFormatted: '0天 00:00:00', isPast: false}
  }
  let endDate

  if (item.isRecurring) {
    // 年度循环：找今年或明年的同月同日
    // ★ 修复：使用 +1 天作为终点，让纪念日当天整日显示为"0天"而非"已过"
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const recurringTarget = parseDateSafe(targetStr)
    const targetMonth = recurringTarget.getMonth()
    const targetDay = recurringTarget.getDate()
    // P1-1修复：2月29日在非闰年→用2月28日（JS new Date会自动偏移到3月1日）
    function getAnniversary(year) {
      if (targetMonth === 1 && targetDay === 29 && !isLeapYear(year)) {
        return new Date(year, 1, 28)
      }
      return new Date(year, targetMonth, targetDay)
    }
    let anniversary = getAnniversary(now.getFullYear())
    if (anniversary < todayStart) {
      // 纪念日本身已过（昨天或更早）→ 推到明年
      anniversary = getAnniversary(now.getFullYear() + 1)
    }
    // endDate = 纪念日次日00:00，保证纪念日当天整日都不算past
    endDate = new Date(anniversary.getFullYear(), anniversary.getMonth(), anniversary.getDate() + 1)
  } else {
    // 一次性倒计时：目标日整天都算“当天”，到次日 00:00 才转为 past
    endDate = new Date(target.getFullYear(), target.getMonth(), target.getDate() + 1)
  }

  const diffMs = endDate.getTime() - now.getTime()
  const isPast = diffMs <= 0
  const absMs = Math.abs(diffMs)

  const days = Math.floor(absMs / (1000 * 60 * 60 * 24))
  const hours = Math.floor((absMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const mins = Math.floor((absMs % (1000 * 60 * 60)) / (1000 * 60))
  const secs = Math.floor((absMs % (1000 * 60)) / 1000)

  const totalFormatted = `${days}天 ${String(hours).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`

  return {days, hours, minutes: mins, seconds: secs, totalFormatted, isPast}
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
  const {startDate, isRecurring, targetDate, direction} = item

  // 累计模式：只要有 startDate，就按照起始日期累计
  if (startDate && typeof startDate === 'string' && startDate.trim() !== '') {
    const start = parseDateSafe(startDate)
    if (!isNaN(start.getTime()) && direction === 'countup') {
      const startDay = new Date(start.getFullYear(), start.getMonth(), start.getDate())
      const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      let totalDays = Math.floor((nowDay.getTime() - startDay.getTime()) / (1000 * 60 * 60 * 24))
      const isPast = totalDays >= 0
      totalDays = Math.abs(totalDays)
      if (isPast) totalDays += 1

      let y = now.getFullYear() - start.getFullYear()
      let m = now.getMonth() - start.getMonth()
      let d = now.getDate() - start.getDate()

      if (d < 0) {
        m -= 1
        const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 0)
        d += prevMonth.getDate()
      }
      if (m < 0) { m += 12; y -= 1 }

      let text
      if (y >= 1) {
        text = `已过去 ${y} 年 ${m} 个月`
      } else if (m >= 1) {
        text = `已过去 ${m} 个月`
      } else {
        text = `已过去 ${totalDays} 天`
      }

      return {text, years: y, months: m, days: d, totalDays, isPast}
    }

    if (!isNaN(start.getTime()) && isRecurring) {
      // 年度循环的已过去时间计算
      let y = now.getFullYear() - start.getFullYear()
      let m = now.getMonth() - start.getMonth()
      let d = now.getDate() - start.getDate()

      if (d < 0) {
        m -= 1
        const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 0)
        d += prevMonth.getDate()
      }
      if (m < 0) { m += 12; y -= 1 }

      // ★ 修复：统一使用零点归一化计算 totalDays，保持与 countup 路径一致
      const startDay = new Date(start.getFullYear(), start.getMonth(), start.getDate())
      const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const totalDays = Math.floor((nowDay.getTime() - startDay.getTime()) / (1000 * 60 * 60 * 24))
      const isPast = true

      let text
      if (y >= 1) {
        text = `已过去 ${y} 年 ${m} 个月`
      } else if (m >= 1) {
        text = `已过去 ${m} 个月`
      } else {
        text = `已过去 ${totalDays} 天`
      }

      return {text, years: y, months: m, days: d, totalDays, isPast}
    }
  }

  // 一次性倒计时（isRecurring=false 或 startDate 无效）
  if (targetDate && typeof targetDate === 'string' && targetDate.trim() !== '') {
    const diff = getDiff(targetDate, now)
    const text = diff.isPast
      ? `已过 ${diff.days} 天`
      : `还有 ${diff.days} 天`
    return {text, years: 0, months: 0, days: diff.days, totalDays: diff.days, isPast: diff.isPast}
  }

  // 兜底：完全无效的数据
  return {text: '还有 0 天', years: 0, months: 0, days: 0, totalDays: 0, isPast: false}
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
  const safeStart = parseDateSafe(startDate)
  if (isNaN(safeStart.getTime())) return null
  for (const milestone of milestones) {
    if (milestone > currentDays) {
      const targetDate = new Date(safeStart)
      targetDate.setDate(targetDate.getDate() + milestone)
      const diff = getDiff(targetDate)
      return {milestone, daysLeft: diff.days, targetDate}
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
  const d = parseDateSafe(date)
  const today = new Date()
  return d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
}

function isTomorrow(date) {
  const d = parseDateSafe(date)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return d.getDate() === tomorrow.getDate() &&
    d.getMonth() === tomorrow.getMonth() &&
    d.getFullYear() === tomorrow.getFullYear()
}

module.exports = {
  getDiff,
  getMainCountdown,
  getElapsedText,
  formatNumber,
  getNextMilestone,
  isToday,
  isTomorrow,
  getCountdownSentence,
  getPreciseCountdown // 兼容旧接口，透传到 getMainCountdown
}
