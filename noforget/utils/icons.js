/**
 * 图标系统 - icons.js
 * 主题风格: apple | notion | airbnb | starbucks
 * 分类: birthday | anniversary | travel | deadline | course | exam | work | custom
 */

// 8个分类
export const CATEGORIES = [
  'birthday', 'anniversary', 'travel', 'deadline',
  'course', 'exam', 'work', 'custom'
];

// 主题列表
export const THEMES = ['apple', 'notion', 'airbnb', 'starbucks'];

/**
 * 获取图标文件本地路径
 * @param {string} theme 主题风格
 * @param {string} category 分类
 * @returns {string} 相对于 static/icons/ 的路径
 */
export function getIconPath(theme, category) {
  return `/static/icons/${category}/${theme}.svg`;
}

/**
 * 获取分类图标名称（emoji 兜底）
 * @param {string} category
 * @returns {string} emoji
 */
export function getCategoryEmoji(category) {
  const map = {
    birthday: '🎂',
    anniversary: '💕',
    travel: '✈️',
    deadline: '⏰',
    course: '📚',
    exam: '📝',
    work: '💼',
    custom: '⭐'
  };
  return map[category] || '📌';
}

/**
 * 获取分类中文名称
 * @param {string} category
 * @returns {string}
 */
export function getCategoryName(category) {
  const map = {
    birthday: '生日',
    anniversary: '纪念日',
    travel: '出行',
    deadline: '截止',
    course: '课程',
    exam: '考试',
    work: '工作',
    custom: '自定义'
  };
  return map[category] || category;
}