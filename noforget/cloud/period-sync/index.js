// cloud/period-sync/index.js
// 姨妈追踪云函数：免登录获取openid + 数据读写
const cloud = require('wx-server-sdk')
cloud.init({env: cloud.DYNAMIC_CURRENT_ENV})

const db = cloud.database()
const COLLECTION = 'periodData'

// 安全字段列表（客户端不可写入）
const PROTECTED_FIELDS = ['_id', '_openid', 'openid', 'createdAt']

// 输入清洗：移除客户端不可写入的字段
function sanitizeData(dirty) {
  if (!dirty || typeof dirty !== 'object') return dirty
  const clean = {...dirty}
  for (const key of Object.keys(clean)) {
    if (PROTECTED_FIELDS.includes(key)) {
      delete clean[key]
    }
  }
  return clean
}

// 云函数入口
exports.main = async (event, _context) => {
  const {action, data} = event
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID // 免鉴权获取用户唯一标识

  if (!openid) {
    return {success: false, error: '无法获取用户身份'}
  }

  try {
    switch (action) {

    // ─── 获取用户所有姨妈数据 ───
    // ✅ P0修复：改用 _openid 字段，与 countdown-sync 保持一致
    case 'get': {
      const record = await db.collection(COLLECTION)
        .where({_openid: openid})
        .limit(1)
        .get()
      return {
        success: true,
        openid,
        data: record.data[0] || null
      }
    }

    // ─── 保存/更新姨妈数据（全量覆盖） ───
    case 'save': {
      if (!data) return {success: false, error: '无数据'}

      const existing = await db.collection(COLLECTION)
        .where({_openid: openid})
        .limit(1)
        .get()

      if (existing.data.length > 0) {
        // 更新已有记录
        await db.collection(COLLECTION)
          .doc(existing.data[0]._id)
          .update({
            data: {
              ...sanitizeData(data),
              updatedAt: db.serverDate()
            }
          })
      } else {
        // 新建记录 — 使用 _openid 而非 openid，保障数据安全规则自动生效
        await db.collection(COLLECTION).add({
          data: {
            _openid: openid,
            ...sanitizeData(data),
            createdAt: db.serverDate(),
            updatedAt: db.serverDate()
          }
        })
      }
      return {success: true, openid}
    }

    // ─── 增量更新（只更新指定字段） ───
    case 'patch': {
      if (!data || Object.keys(data).length === 0) {
        return {success: false, error: '无更新字段'}
      }
      const existing = await db.collection(COLLECTION)
        .where({_openid: openid})
        .limit(1)
        .get()

      if (existing.data.length > 0) {
        await db.collection(COLLECTION)
          .doc(existing.data[0]._id)
          .update({
            data: {
              ...sanitizeData(data),
              updatedAt: db.serverDate()
            }
          })
        return {success: true, openid}
      }

      await db.collection(COLLECTION).add({
        data: {
          _openid: openid,
          ...sanitizeData(data),
          entries: data.entries || [],
          daily: data.daily || {},
          settings: data.settings || {},
          version: data.version || 1,
          createdAt: db.serverDate(),
          updatedAt: db.serverDate()
        }
      })
      return {success: true, openid, created: true}
    }

    // ─── 获取openid（其他操作的认证凭证） ───
    case 'whoami': {
      return {success: true, openid}
    }

    case 'deleteAll': {
      // ✅ P0修复：删除用户全部云端姨妈数据
      const existing = await db.collection(COLLECTION)
        .where({_openid: openid})
        .limit(1)
        .get()
      if (existing.data.length > 0) {
        await db.collection(COLLECTION).doc(existing.data[0]._id).remove()
        return {success: true, removed: 1}
      }
      return {success: true, removed: 0}
    }

    default:
      return {success: false, error: `未知操作: ${action}`}
    }
  } catch (err) {
    console.error('period-sync error:', err)
    return {success: false, error: err.message || '服务器错误'}
  }
}
