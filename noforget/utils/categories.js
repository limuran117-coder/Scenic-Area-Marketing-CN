// utils/categories.js - 倒计时分类配置

const categories = [
  {
    id: 'birthday',
    name: '生日',
    icon: '🎂',
    emoji: '🎂',
    direction: 'countdown', // 默认倒计时
    theme: 'morandi', // 推荐主题
    color: '#FFB6C1'
  },
  {
    id: 'love',
    name: '恋爱开始',
    icon: '💕',
    emoji: '💕',
    direction: 'countup', // 默认正向计时
    theme: 'morandi',
    color: '#FF69B4'
  },
  {
    id: 'wedding',
    name: '结婚纪念日',
    icon: '💒',
    emoji: '💒',
    direction: 'countup',
    theme: 'apple',
    color: '#C9A0DC'
  },
  {
    id: 'parent_birthday',
    name: '父母生日',
    icon: '❤️',
    emoji: '❤️',
    direction: 'countdown',
    theme: 'vintage',
    color: '#FFA07A'
  },

  {
    id: 'child_birthday',
    name: '孩子生日',
    icon: '🍼',
    emoji: '🍼',
    direction: 'countdown',
    theme: 'morandi',
    color: '#87CEEB'
  },
  {
    id: 'pet_birthday',
    name: '宠物生日',
    icon: '🐾',
    emoji: '🐾',
    direction: 'countdown',
    theme: 'morandi',
    color: '#98FB98'
  },
  {
    id: 'death',
    name: '忌日',
    icon: '🙏',
    emoji: '🙏',
    direction: 'countup', // 正向计时，已过多少年
    theme: 'apple',
    color: '#C0C0C0',
    isMourning: true // 特殊标记
  },
  {
    id: 'important_person',
    name: '重要的人',
    icon: '👤',
    emoji: '👤',
    direction: 'countup',
    theme: 'apple',
    color: '#B0C4DE'
  },
  {
    id: 'goal',
    name: '目标达成',
    icon: '🏆',
    emoji: '🏆',
    direction: 'countdown',
    theme: 'vintage',
    color: '#FFD700'
  },
  {
    id: 'travel',
    name: '旅行出发',
    icon: '✈️',
    emoji: '✈️',
    direction: 'countdown',
    theme: 'morandi',
    color: '#87CEFA'
  },

  {
    id: 'graduation',
    name: '毕业',
    icon: '🎓',
    emoji: '🎓',
    direction: 'countdown',
    theme: 'morandi',
    color: '#778899'
  },
  {
    id: 'work_anniversary',
    name: '工作纪念日',
    icon: '💼',
    emoji: '💼',
    direction: 'countup',
    theme: 'apple',
    color: '#4682B4'
  },
  {
    id: 'festival',
    name: '节日',
    icon: '🎊',
    emoji: '🎊',
    direction: 'countdown',
    theme: 'vintage',
    color: '#FF6347'
  }
]

// 根据ID获取分类
function getCategoryById(id) {
  return categories.find(c => c.id === id) || categories[0]
}

// 获取所有分类
function getAllCategories() {
  return categories
}

module.exports = {
  categories,
  getCategoryById,
  getAllCategories
}
