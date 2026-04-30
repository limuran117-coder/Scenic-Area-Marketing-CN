// utils/countdown.js - 倒计时/正向计时核心算法

/**
 * 计算两个日期之间的差值
 * @param {Date} targetDate - 目标日期
 * @param {Date} nowDate - 当前日期（可选，默认现在）
 * @returns {Object} 差值对象
 */
function getDiff(targetDate, nowDate = new Date()) {
  const target = new Date(targetDate)
  const now = new Date(nowDate)
  
  // 重置时间到00:00:00进行日期计算
  const targetDay = new Date(target.getFullYear(), target.getMonth(), target.getDate())
  const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  const diffMs = targetDay.getTime() - nowDay.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  return {
    days: Math.abs(diffDays),
    isPast: diffMs < 0, // 是否已过
    diffMs: diffMs
  }
}

/**
 * 计算精确的年月日时分秒差值
 * @param {Date} targetDate - 目标日期
 * @param {Date} nowDate - 当前日期
 * @returns {Object} 精确差值
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
  if (seconds < 0) {
    seconds += 60
    minutes -= 1
  }
  if (minutes < 0) {
    minutes += 60
    hours -= 1
  }
  if (hours < 0) {
    hours += 24
    days -= 1
  }
  if (days < 0) {
    // 借位计算
    const lastMonth = new Date(target.getFullYear(), target.getMonth(), 0)
    days += lastMonth.getDate()
    months -= 1
  }
  if (months < 0) {
    months += 12
    years -= 1
  }
  
  const isPast = target.getTime() < now.getTime()
  
  // 如果已过，转换为正数
  if (isPast) {
    years = Math.abs(years)
    months = Math.abs(months)
    days = Math.abs(days)
    hours = Math.abs(hours)
    minutes = Math.abs(minutes)
    seconds = Math.abs(seconds)
  }
  
  return {
    years,
    months,
    days,
    hours,
    minutes,
    seconds,
    totalDays: Math.floor(Math.abs(target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)),
    isPast,
    rawDiff: target.getTime() - now.getTime()
  }
}

/**
 * 格式化显示文本（简洁版）
 * @param {Object} diff - getExactDiff返回的对象
 * @param {Boolean} isCountUp - 是否是正向计时
 * @returns {String} 格式化字符串
 */
function formatDisplayText(diff, isCountUp = false) {
  if (diff.isPast || isCountUp) {
    // 正向计时 / 已过日期
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
    // 倒计时
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
 * 格式化数字（添加千位分隔符）
 * @param {Number} num 
 * @returns {String}
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 获取下一个纪念日的倒计时（100天、1000天等）
 * @param {Date} startDate - 起始日期
 * @param {Number} currentDays - 当前天数
 * @returns {Object} 下一个里程碑
 */
function getNextMilestone(startDate, currentDays) {
  const milestones = [100, 200, 365, 500, 666, 1000, 1500, 2000, 3000, 3650, 5000, 10000]
  
  for (const milestone of milestones) {
    if (milestone > currentDays) {
      const targetDate = new Date(startDate)
      targetDate.setDate(targetDate.getDate() + milestone)
      const diff = getDiff(targetDate)
      return {
        milestone,
        daysLeft: diff.days,
        targetDate: targetDate
      }
    }
  }
  return null
}

/**
 * 判断是否是今天
 * @param {Date} date 
 * @returns {Boolean}
 */
function isToday(date) {
  const d = new Date(date)
  const today = new Date()
  return d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
}

/**
 * 判断是否是明天
 * @param {Date} date 
 * @returns {Boolean}
 */
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
  formatDisplayText,
  formatNumber,
  getNextMilestone,
  isToday,
  isTomorrow
}
