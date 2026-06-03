// cloud/send-reminder/index.js
// 姨妈+纪念日订阅消息定时提醒云函数
// 触发规则：每天早上9:00检查所有订阅用户，发送姨妈提醒 + 纪念日倒计时提醒
const cloud = require('wx-server-sdk')
cloud.init({env: cloud.DYNAMIC_CURRENT_ENV})

const db = cloud.database()
const COLLECTION = 'periodData'
const COUNTDOWN_COLLECTION = 'countdownItems'

// ─── 模板ID（微信公众平台 → 订阅消息 → 我的模板）──────────
const TEMPLATES = {
  // 姨妈提醒模板（keyword: date1/phrase2/thing3）
  PERIOD: 'L6aIoXgdKCQpd6wuR1VGYLzQLDZq6SsLlqDdffI8s7w',
  // 纪念日倒计时模板（keyword: 名称/具体日期/天数/温馨提示）
  COUNTDOWN: 'L6aIoXgdKCQpd6wuR1VGYDUZTWngDH1TfJh90aVtWh0',
}

// ─── 周期计算工具 ──────────────────────────────
function parseDateSafe(value) {
  if (!value) return null
  const normalized = String(value).replace(/-/g, '/')
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

function daysBetween(dateA, dateB) {
  const a = parseDateSafe(dateA)
  const b = parseDateSafe(dateB)
  if (!a || !b) return null
  return Math.floor(Math.abs(a - b) / (1000 * 60 * 60 * 24))
}

function getCycleIntervals(entries = []) {
  const sorted = entries
    .slice()
    .sort((a, b) => new Date(String(b.startDate).replace(/-/g, '/')) - new Date(String(a.startDate).replace(/-/g, '/')))

  const intervals = []
  for (let i = 0; i < sorted.length - 1; i++) {
    const length = daysBetween(sorted[i].startDate, sorted[i + 1].startDate)
    if (!Number.isFinite(length) || length <= 0) continue
    intervals.push(length)
  }
  return {sorted, intervals}
}

function getPredictedNextPeriod(entries = [], settings = {}) {
  const {sorted, intervals} = getCycleIntervals(entries)
  if (!sorted.length) return null

  let cycleLength = Number(settings.cycleLength) || 28
  if (intervals.length > 0) {
    const recent = intervals.slice(0, Math.min(6, intervals.length))
    let avg = recent.reduce((sum, item) => sum + item, 0) / recent.length
    if (recent.length >= 3) {
      avg += (recent[0] - recent[1]) / recent.length
    }
    cycleLength = Math.round(avg)
  }

  cycleLength = Math.max(21, Math.min(35, cycleLength))
  const last = parseDateSafe(sorted[0].startDate)
  if (!last) return null
  const next = new Date(last)
  next.setDate(next.getDate() + cycleLength)
  return next
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function getDaysUntil(targetDate) {
  if (!targetDate) return null
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const target = new Date(targetDate)
  target.setHours(0, 0, 0, 0)
  const diff = target - now
  return Math.round(diff / (1000 * 60 * 60 * 24))
}

function shouldSendReminder(daysLeft, settings = {}) {
  const remindEnabled = settings.remindEnabled !== false
  const remindOnDay = settings.remindOnDay !== false
  const remindDays = Number.isFinite(settings.remindBefore) ? settings.remindBefore : 1

  if (!remindEnabled) return false
  if (daysLeft === 0) return remindOnDay
  return daysLeft === remindDays
}

// ─── 发送订阅消息 ──────────────────────────────
async function sendPeriodReminder(openid, predictedDateStr, daysLeft) {
  try {
    const result = await cloud.openapi.subscribeMessage.send({
      touser: openid,
      template_id: TEMPLATES.PERIOD,
      page: 'pages/period/period',
      data: {
        date1: {value: predictedDateStr},
        phrase2: {value: daysLeft === 0 ? '就是今天' : `还有${daysLeft}天`},
        thing3: {value: '姨妈快要来了，记得提前准备好哦'}
      }
    })
    console.log(`[${openid}] 姨妈提醒发送成功:`, result)
    return {success: true}
  } catch (err) {
    console.error(`[${openid}] 姨妈提醒发送失败:`, err)
    return {success: false, error: err.message}
  }
}

// ─── 纪念日提醒发送 ──────────────────────────────
async function sendCountdownReminder(openid, item, daysLeft) {
  const title = (item && item.title) || '纪念日'
  const targetDate = (item && item.targetDate) || ''
  const COUNTDOWN_TEMPLATE_ID = TEMPLATES.COUNTDOWN

  if (!COUNTDOWN_TEMPLATE_ID) {
    console.log(`[${openid}] 纪念日「${title}」距${targetDate}还有${daysLeft}天 (模板ID未配置，跳过发送)`)
    return {success: false, error: 'template-not-configured', skipped: true}
  }

  try {
    const result = await cloud.openapi.subscribeMessage.send({
      touser: openid,
      template_id: COUNTDOWN_TEMPLATE_ID,
      page: `/pages/detail/detail?id=${item.id || ''}`,
      data: {
        thing1: {value: title},
        date2: {value: targetDate},
        phrase3: {value: daysLeft === 0 ? '就是今天' : `还有${daysLeft}天`},
        thing4: {value: '别忘了这个重要的日子哦'}
      }
    })
    console.log(`[${openid}] 纪念日提醒「${title}」发送成功:`, result)
    return {success: true}
  } catch (err) {
    console.error(`[${openid}] 纪念日提醒「${title}」发送失败:`, err)
    return {success: false, error: err.message}
  }
}

// ─── 分页查询所有纪念日（修复：支持分页，不限于500条）──────
async function listAllCountdownItems() {
  const allItems = []
  let hasMore = true
  let skip = 0
  const BATCH_SIZE = 100

  while (hasMore) {
    try {
      const res = await db.collection(COUNTDOWN_COLLECTION)
        .where({})
        .field({_openid: true, id: true, title: true, targetDate: true, remindDays: true, categoryId: true})
        .skip(skip)
        .limit(BATCH_SIZE)
        .get()
      const items = res.data || []
      if (items.length > 0) {
        allItems.push(...items)
        skip += items.length
      }
      hasMore = items.length >= BATCH_SIZE
    } catch (e) {
      console.error('[send-reminder] listAllCountdownItems 分页查询失败:', e.message)
      break
    }
  }

  return {data: allItems}
}

// ─── 获取用户 openid（兼容 openid 和 _openid 字段）────────
function getUserId(user) {
  return user.openid || user._openid || null
}

// ─── 云函数入口 ──────────────────────────────
exports.main = async (_event, _context) => {
  const wxContext = cloud.getWXContext()
  const triggerdBy = wxContext.triggeredBy || 'scheduled'
  console.log(`[send-reminder] 触发来源: ${triggerdBy}, 时间: ${new Date().toISOString()}`)

  try {
    // 1. 分页查询所有已开启订阅的用户
    const allUsers = []
    let hasMore = true
    let skip = 0

    // ✅ P0#2 修复：查询时同时获取 openid 和 _openid，兼容两种字段命名
    while (hasMore) {
      const {data: users} = await db.collection(COLLECTION)
        .where({subscribed: true})
        .field({openid: true, _openid: true, entries: true, settings: true})
        .skip(skip)
        .limit(100)
        .get()
      if (users && users.length > 0) {
        allUsers.push(...users)
        skip += users.length
      }
      hasMore = users && users.length >= 100
    }

    console.log(`[send-reminder] 共 ${allUsers.length} 位订阅用户`)

    if (allUsers.length === 0) {
      return {success: true, message: '无订阅用户'}
    }

    // 2. 遍历每个用户，检查是否需要提醒
    const results = []

    for (const user of allUsers) {
      const openid = getUserId(user)
      const {entries, settings = {}} = user

      if (!openid || !entries || entries.length === 0) continue

      // 计算下次姨妈日期
      const nextPeriod = getPredictedNextPeriod(entries, settings)
      if (!nextPeriod) continue

      // 计算距离天数
      const daysLeft = getDaysUntil(nextPeriod)
      if (daysLeft === null) continue

      console.log(`[${openid}] 下次: ${formatDate(nextPeriod)}, 剩余: ${daysLeft}天, 提醒阈值: ${settings.remindBefore ?? 1}天`)

      // 3. 判断是否发送：当天 或 提前 N 天
      if (shouldSendReminder(daysLeft, settings)) {
        const predictedStr = formatDate(nextPeriod)
        const sendResult = await sendPeriodReminder(openid, predictedStr, daysLeft)
        results.push({openid, daysLeft, ...sendResult})
      } else {
        results.push({openid, daysLeft, skipped: true})
      }
    }

    // 3. 纪念日倒计时提醒（✅ P0#1修复：使用专用 COUNTDOWN 模板ID，不再混用姨妈模板）
    let countdownSent = 0
    let countdownFailed = 0
    let countdownSkippedNoTemplate = 0

    if (TEMPLATES.COUNTDOWN) {
      try {
        const {data: countdownItems} = await listAllCountdownItems()

        if (countdownItems && countdownItems.length > 0) {
          console.log(`[send-reminder] 倒计时提醒: ${countdownItems.length} 个候选项`)

          for (const item of countdownItems) {
            if (!item._openid || item.remindDays === undefined || item.remindDays === null) continue

            const targetDate = parseDateSafe(item.targetDate)
            if (!targetDate) continue

            const daysLeft = getDaysUntil(targetDate)
            if (daysLeft === null || daysLeft < 0) continue

            const rd = Number(item.remindDays)
            if (!Number.isFinite(rd)) continue
            if (daysLeft !== rd) continue

            // ✅ 去重保护：检查今日是否已发送过
            const todayStart = new Date()
            todayStart.setHours(0, 0, 0, 0)
            if (item.lastRemindedAt && item.lastRemindedAt >= todayStart.getTime()) {
              console.log(`[${item._openid}] 纪念日「${item.title}」今日已发送，跳过`)
              countdownSent++
              continue
            }

            const result = await sendCountdownReminder(item._openid, item, daysLeft)
            if (result.success) {
              // 记录发送时间，防止重复
              try {
                await db.collection(COUNTDOWN_COLLECTION).doc(item._id).update({
                  data: {lastRemindedAt: Date.now()}
                })
              } catch (e) {
                console.warn(`[send-reminder] lastRemindedAt更新失败:`, e.message)
              }
              countdownSent++
            } else if (!result.skipped) {
              countdownFailed++
            }
          }
        }
      } catch (e) {
        console.error('[send-reminder] 倒计时提醒模块错误:', e.message)
      }
    } else {
      countdownSkippedNoTemplate = 1
      console.log('[send-reminder] COUNTDOWN模板ID未配置，跳过纪念日倒计时提醒')
    }

    // 4. 汇总结果
    const sent = results.filter(r => r.success).length
    const failed = results.filter(r => !r.success && !r.skipped).length
    console.log(`[send-reminder] 完成: 发送${sent}条, 失败${failed}条`)

    return {
      success: true,
      total: allUsers.length,
      periodSent: sent,
      periodFailed: failed,
      countdownSent,
      countdownFailed,
      countdownSkippedNoTemplate,
      details: results.slice(0, 10)
    }

  } catch (err) {
    console.error('[send-reminder] 错误:', err)
    return {success: false, error: err.message}
  }
}
