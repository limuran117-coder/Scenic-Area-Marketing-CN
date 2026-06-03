const cloud = require('wx-server-sdk')

cloud.init({env: cloud.DYNAMIC_CURRENT_ENV})

const db = cloud.database()
const COLLECTION = 'countdownItems'
const PAGE_SIZE = 100

function sanitizeItem(item) {
  if (!item || typeof item !== 'object') return null
  const normalized = {...item}
  delete normalized._id
  delete normalized._openid
  return normalized
}

async function listAllByOpenid(openid) {
  const results = []
  let skip = 0

  while (true) {
    const res = await db.collection(COLLECTION)
      .where({_openid: openid})
      .orderBy('updatedAt', 'desc')
      .skip(skip)
      .limit(PAGE_SIZE)
      .get()
    const batch = Array.isArray(res.data) ? res.data : []
    results.push(...batch)
    if (batch.length < PAGE_SIZE) break
    skip += batch.length
  }

  return results
}

exports.main = async (event, _context) => {
  const {action, data} = event || {}
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID

  if (!openid) {
    return {success: false, error: '无法获取用户身份'}
  }

  try {
    switch (action) {
    case 'whoami':
      return {success: true, openid}

    case 'deleteAll': {
      // ✅ P0修复：删除用户全部云端数据
      const allDocs = await listAllByOpenid(openid)
      if (allDocs.length > 0) {
        await Promise.all(allDocs.map(doc =>
          db.collection(COLLECTION).doc(doc._id).remove().catch(() => null)
        ))
      }
      return {success: true, removed: allDocs.length}
    }

    case 'list': {
      const docs = await listAllByOpenid(openid)
      return {
        success: true,
        openid,
        items: docs.map(sanitizeItem).filter(Boolean)
      }
    }

    case 'upsert': {
      const item = sanitizeItem(data && data.item)
      if (!item || !item.id) {
        return {success: false, error: '缺少有效纪念日数据'}
      }

      // ★ 修复：云函数端必须显式写入 _openid（服务端不会自动添加）
      const docData = {
        ...item,
        _openid: openid,
        createdAt: item.createdAt || Date.now(),
        updatedAt: db.serverDate()
      }

      const existing = await db.collection(COLLECTION)
        .where({_openid: openid, id: item.id})
        .limit(PAGE_SIZE)
        .get()
      const docs = Array.isArray(existing.data) ? existing.data : []

      if (docs.length > 0) {
        await db.collection(COLLECTION).doc(docs[0]._id).update({
          data: docData
        })

        if (docs.length > 1) {
          await Promise.all(
            docs.slice(1).map(doc => db.collection(COLLECTION).doc(doc._id).remove().catch(() => null))
          )
        }
      } else {
        await db.collection(COLLECTION).add({
          data: docData
        })
      }

      return {success: true, openid, item}
    }

    case 'delete': {
      const id = data && data.id
      if (!id) {
        return {success: false, error: '缺少纪念日ID'}
      }

      const existing = await db.collection(COLLECTION)
        .where({_openid: openid, id})
        .limit(PAGE_SIZE)
        .get()
      const docs = Array.isArray(existing.data) ? existing.data : []
      await Promise.all(docs.map(doc => db.collection(COLLECTION).doc(doc._id).remove().catch(() => null)))
      return {success: true, openid, removed: docs.length}
    }

    default:
      return {success: false, error: `未知操作: ${action}`}
    }
  } catch (error) {
    console.error('countdown-sync error:', error)
    return {success: false, error: error.message || '服务器错误'}
  }
}