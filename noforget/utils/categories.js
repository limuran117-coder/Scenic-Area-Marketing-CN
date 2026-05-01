// utils/categories.js - 分类配置（含 isRecurring 标记）

// 需要年度循环的分类：每年重复，到当年月日
const RECURRING_CATEGORIES = new Set([
  'birthday', 'love', 'wedding', 'parent_birthday',
  'child_birthday', 'pet_birthday', 'death',
  'important_person', 'work_anniversary', 'festival'
])

const categories = [
  {
    id: 'birthday',
    name: '生日',
    icon: '🎂',
    direction: 'countup',      // 旧字段，已被 isRecurring 替代
    isRecurring: true,         // ★ 每年循环
    theme: 'apple',
    color: '#FFB6C1'
  },
  {
    id: 'love',
    name: '恋爱开始',
    icon: '💕',
    direction: 'countup',
    isRecurring: true,          // ★ 每年循环
    theme: 'airbnb',
    color: '#FF69B4'
  },
  {
    id: 'wedding',
    name: '结婚纪念日',
    icon: '💒',
    direction: 'countup',
    isRecurring: true,         // ★ 每年循环
    theme: 'apple',
    color: '#C9A0DC'
  },
  {
    id: 'death',
    name: '忌日',
    icon: '🙏',
    direction: 'countup',
    isRecurring: true,         // ★ 每年循环（纪念逝者，每年当天）
    theme: 'notion',
    color: '#B0A0C0'
  },
  {
    id: 'pet_birthday',
    name: '宠物生日',
    icon: '🐾',
    direction: 'countup',
    isRecurring: true,         // ★ 每年循环
    theme: 'airbnb',
    color: '#98FB98'
  },
  {
    id: 'parent_birthday',
    name: '父母生日',
    icon: '❤️',
    direction: 'countdown',
    isRecurring: true,
    theme: 'starbucks',
    color: '#FFA07A'
  },
  {
    id: 'child_birthday',
    name: '孩子生日',
    icon: '🍼',
    direction: 'countdown',
    isRecurring: true,
    theme: 'airbnb',
    color: '#87CEEB'
  },
  {
    id: 'important_person',
    name: '重要的人',
    icon: '👤',
    direction: 'countup',
    isRecurring: true,
    theme: 'apple',
    color: '#B0C4DE'
  },
  {
    id: 'work_anniversary',
    name: '工作纪念日',
    icon: '💼',
    direction: 'countup',
    isRecurring: true,
    theme: 'starbucks',
    color: '#4682B4'
  },
  {
    id: 'festival',
    name: '节日',
    icon: '🎊',
    direction: 'countdown',
    isRecurring: true,
    theme: 'airbnb',
    color: '#FF6347'
  },
  // 以下为一次性倒计时（isRecurring=false，默认值）
  {
    id: 'goal',
    name: '目标达成',
    icon: '🏆',
    direction: 'countdown',
    isRecurring: false,
    theme: 'starbucks',
    color: '#FFD700'
  },
  {
    id: 'travel',
    name: '旅行出发',
    icon: '✈️',
    direction: 'countdown',
    isRecurring: false,
    theme: 'airbnb',
    color: '#87CEFA'
  },
  {
    id: 'graduation',
    name: '毕业',
    icon: '🎓',
    direction: 'countdown',
    isRecurring: false,
    theme: 'notion',
    color: '#778899'
  }
]

function getCategoryById(id) {
  return categories.find(c => c.id === id) || categories[0]
}

function getAllCategories() {
  return categories
}

function isRecurringCategory(categoryId) {
  return RECURRING_CATEGORIES.has(categoryId)
}

const themeIconStyles = {
  apple:      { fontSize: 18, opacity: 1.0 },
  notion:     { fontSize: 16, opacity: 0.85 },
  airbnb:     { fontSize: 20, opacity: 1.0 },
  starbucks:  { fontSize: 18, opacity: 0.95 }
}

function getIconStyle(themeId, categoryColor) {
  const style = themeIconStyles[themeId] || themeIconStyles.apple
  return { fontSize: style.fontSize, opacity: style.opacity, color: categoryColor }
}

module.exports = {
  categories,
  getCategoryById,
  getAllCategories,
  isRecurringCategory,
  themeIconStyles,
  getIconStyle,
  RECURRING_CATEGORIES
}
