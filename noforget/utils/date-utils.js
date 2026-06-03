// utils/date-utils.js — 统一日期解析（消除5份重复实现）
// 合并自: utils/countdown.js, utils/period.js, pages/detail/detail.js,
//         pages/reminder/reminder.js, cloud/send-reminder/index.js

/**
 * iOS 安全日期解析：'YYYY-MM-DD' → Date
 * iOS Safari 不认横杠，换成斜杠后构造避免 NaN
 */
function parseDateSafe(value) {
  if (!value) return new Date(NaN)
  if (value instanceof Date) return new Date(value.getTime())
  if (typeof value !== 'string') {
    const d = new Date(value)
    return isNaN(d.getTime()) ? new Date(NaN) : d
  }
  const normalized = String(value).replace(/-/g, '/')
  const d = new Date(normalized)
  return isNaN(d.getTime()) ? new Date(NaN) : d
}

/**
 * 两个日期之间的天数差
 */
function daysBetween(dateA, dateB) {
  const a = parseDateSafe(dateA)
  const b = parseDateSafe(dateB)
  const diff = Math.abs(a - b)
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

/**
 * 日期加 N 天，返回 YYYY-MM-DD 字符串
 */
function addDays(dateStr, days) {
  const d = parseDateSafe(dateStr)
  d.setDate(d.getDate() + days)
  return formatDate(d)
}

/**
 * Date → 'YYYY-MM-DD'
 */
function formatDate(date) {
  const d = date instanceof Date ? date : parseDateSafe(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/**
 * Date → 'MM.DD'
 */
function formatMonthDay(dateStr) {
  if (!dateStr) return '—'
  const d = parseDateSafe(dateStr)
  return `${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

module.exports = {
  parseDateSafe,
  daysBetween,
  addDays,
  formatDate,
  formatMonthDay
}
