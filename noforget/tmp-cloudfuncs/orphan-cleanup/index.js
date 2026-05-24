const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const _ = db.command
const SOURCE = 'countdownItems'
const BACKUP = 'countdownItems_orphaned_backup'
const PAGE_SIZE = 100

async function ensureBackupCollection() {
  try {
    await db.createCollection(BACKUP)
    return { created: true }
  } catch (error) {
    const msg = String(error && (error.errMsg || error.message || error.stack || error))
    if (
      msg.includes('collection already exists') ||
      msg.includes('already exists') ||
      msg.includes('集合已存在') ||
      msg.includes('ResourceExist') ||
      msg.includes('DATABASE_COLLECTION_ALREADY_EXIST') ||
      msg.includes('-501001')
    ) {
      return { created: false, existed: true }
    }
    throw error
  }
}

async function listOrphans() {
  const res = await db.collection(SOURCE)
    .where({ _openid: _.exists(false) })
    .limit(PAGE_SIZE)
    .get()
  return Array.isArray(res.data) ? res.data : []
}

async function listBackup() {
  const res = await db.collection(BACKUP).limit(200).get()
  return Array.isArray(res.data) ? res.data : []
}

exports.main = async (event) => {
  const action = event && event.action
  if (action === 'backup') {
    await ensureBackupCollection()
    const orphans = await listOrphans()
    if (!orphans.length) return { success: true, action, orphanCount: 0, backupInserted: 0 }

    const payload = orphans.map((doc) => ({
      originalId: doc._id,
      backupAt: db.serverDate(),
      sourceCollection: SOURCE,
      orphanSnapshot: doc
    }))
    const result = await db.collection(BACKUP).add({ data: payload })
    const backupDocs = await listBackup()
    return {
      success: true,
      action,
      orphanCount: orphans.length,
      backupInserted: Array.isArray(result && result._ids) ? result._ids.length : payload.length,
      backupCount: backupDocs.length,
      sampleOriginalIds: orphans.slice(0, 5).map((d) => d._id)
    }
  }

  if (action === 'verify') {
    const orphans = await listOrphans()
    const backupDocs = await listBackup()
    return {
      success: true,
      action,
      orphanCount: orphans.length,
      backupCount: backupDocs.length,
      backupOriginalIds: backupDocs.slice(0, 10).map((d) => d.originalId)
    }
  }

  if (action === 'cleanup') {
    const orphans = await listOrphans()
    const removed = await Promise.all(
      orphans.map((doc) => db.collection(SOURCE).doc(doc._id).remove().then(() => doc._id).catch(() => null))
    )
    const remain = await listOrphans()
    return {
      success: true,
      action,
      removedCount: removed.filter(Boolean).length,
      remainingCount: remain.length,
      removedIdsSample: removed.filter(Boolean).slice(0, 10)
    }
  }

  return { success: false, error: `unknown action: ${action || ''}` }
}
