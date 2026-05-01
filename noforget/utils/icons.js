/**
 * 图标系统 - icons.js
 * 主题风格: apple | notion | airbnb | starbucks
 * 分类: birthday | love | wedding | death | pet_birthday | parent_birthday | child_birthday | important_person | work_anniversary | festival | goal | travel | graduation
 *
 * 注意：图标文件可能不存在，此时 image 标签会静默失败，
 * 分类 emoji（cat.icon）作为兜底显示在文字标签旁。
 * iconPath 用于需要小图标的场景（如卡片分类标签旁）。
 */

const CATEGORIES = [
  'birthday', 'love', 'wedding', 'death', 'pet_birthday',
  'parent_birthday', 'child_birthday', 'important_person',
  'work_anniversary', 'festival', 'goal', 'travel', 'graduation'
]

const THEMES = ['apple', 'notion', 'airbnb', 'starbucks']

/**
 * 获取图标文件本地路径
 * 如果文件不存在，调用方应使用 emoji（cat.icon）兜底
 * @param {string} theme 主题风格
 * @param {string} category 分类ID
 * @returns {string} 相对于 static/icons/ 的路径
 */
function getIconPath(theme, category) {
  // 图标文件存储在 /pages/index/static/icons/[category]/[theme].svg
  // 如果文件不存在，image 标签会静默失败
  return `/pages/index/static/icons/${category}/${theme}.svg`
}

/**
 * 获取分类 emoji（兜底）
 * @param {string} category
 * @returns {string} emoji
 */
function getCategoryEmoji(category) {
  const map = {
    birthday:         '🎂',
    love:             '💕',
    wedding:          '💒',
    death:            '🙏',
    pet_birthday:     '🐾',
    parent_birthday:  '❤️',
    child_birthday:   '🍼',
    important_person: '👤',
    work_anniversary: '💼',
    festival:         '🎊',
    goal:             '🏆',
    travel:           '✈️',
    graduation:       '🎓'
  }
  return map[category] || '📌'
}

/**
 * 获取分类中文名称
 * @param {string} category
 * @returns {string}
 */
function getCategoryName(category) {
  const map = {
    birthday:         '生日',
    love:             '恋爱开始',
    wedding:          '结婚纪念日',
    death:            '忌日',
    pet_birthday:     '宠物生日',
    parent_birthday:  '父母生日',
    child_birthday:   '孩子生日',
    important_person: '重要的人',
    work_anniversary: '工作纪念日',
    festival:         '节日',
    goal:             '目标达成',
    travel:           '旅行出发',
    graduation:       '毕业'
  }
  return map[category] || category
}

module.exports = {
  CATEGORIES,
  THEMES,
  getIconPath,
  getCategoryEmoji,
  getCategoryName
}