/**
 * utils/theme.js - 主题系统核心
 * 提供四套主题的完整数据（cssVars + 扁平颜色对象）
 */

const themes = {
  apple: {
    id: 'apple',
    name: 'Apple',
    cssVars: `
      --theme-accent: #0066cc;
      --theme-accent-rgb: 0,102,204;
      --theme-accent-light: rgba(0,102,204,0.12);
      --theme-text-primary: #1d1d1f;
      --theme-text-secondary: #6e6e73;
      --theme-text-accent: #0066cc;
      --theme-background: #ffffff;
      --theme-card-bg: #ffffff;
      --theme-border: rgba(0,0,0,0.08);
      --theme-shadow: 0 2px 8px rgba(0,0,0,0.08);
      --theme-shadow-card: 0 4px 16px rgba(0,0,0,0.1);
      --theme-radius-card: 16px;
      --theme-radius-btn: 12px;
      --theme-icon-color: #1d1d1f;
      --theme-duration-micro: 150ms;
      --theme-ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
    `,
    background: '#ffffff',
    cardBg: '#ffffff',
    textPrimary: '#1d1d1f',
    textSecondary: '#6e6e73',
    textAccent: '#0066cc',
    border: 'rgba(0,0,0,0.08)',
    shadow: '0 2px 8px rgba(0,0,0,0.08)',
    shadowCard: '0 4px 16px rgba(0,0,0,0.1)',
    radiusCard: '16px',
    radiusBtn: '12px',
    accentColor: '#0066cc',
  },

  notion: {
    id: 'notion',
    name: 'Notion',
    cssVars: `
      --theme-accent: #2385e2;
      --theme-accent-rgb: 35,133,226;
      --theme-accent-light: rgba(35,133,226,0.1);
      --theme-text-primary: rgba(0,0,0,0.88);
      --theme-text-secondary: #9c9489;
      --theme-text-accent: #2385e2;
      --theme-background: #faf9f7;
      --theme-card-bg: #ffffff;
      --theme-border: rgba(0,0,0,0.07);
      --theme-shadow: 0 1px 4px rgba(0,0,0,0.06);
      --theme-shadow-card: 0 2px 8px rgba(0,0,0,0.07);
      --theme-radius-card: 10px;
      --theme-radius-btn: 8px;
      --theme-icon-color: rgba(0,0,0,0.75);
      --theme-duration-micro: 150ms;
      --theme-ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
    `,
    background: '#faf9f7',
    cardBg: '#ffffff',
    textPrimary: 'rgba(0,0,0,0.88)',
    textSecondary: '#9c9489',
    textAccent: '#2385e2',
    border: 'rgba(0,0,0,0.07)',
    shadow: '0 1px 4px rgba(0,0,0,0.06)',
    shadowCard: '0 2px 8px rgba(0,0,0,0.07)',
    radiusCard: '10px',
    radiusBtn: '8px',
    accentColor: '#2385e2',
  },

  airbnb: {
    id: 'airbnb',
    name: 'Airbnb',
    cssVars: `
      --theme-accent: #ff385c;
      --theme-accent-rgb: 255,56,92;
      --theme-accent-light: rgba(255,56,92,0.1);
      --theme-text-primary: #1a1a1a;
      --theme-text-secondary: #717171;
      --theme-text-accent: #ff385c;
      --theme-background: #fafafa;
      --theme-card-bg: #ffffff;
      --theme-border: #f0f0f0;
      --theme-shadow: 0 2px 8px rgba(0,0,0,0.08);
      --theme-shadow-card: 0 4px 16px rgba(0,0,0,0.1);
      --theme-radius-card: 24px;
      --theme-radius-btn: 16px;
      --theme-icon-color: #ff385c;
      --theme-duration-micro: 150ms;
      --theme-ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
    `,
    background: '#fafafa',
    cardBg: '#ffffff',
    textPrimary: '#1a1a1a',
    textSecondary: '#717171',
    textAccent: '#ff385c',
    border: '#f0f0f0',
    shadow: '0 2px 8px rgba(0,0,0,0.08)',
    shadowCard: '0 4px 16px rgba(0,0,0,0.1)',
    radiusCard: '24px',
    radiusBtn: '16px',
    accentColor: '#ff385c',
  },

  starbucks: {
    id: 'starbucks',
    name: 'Starbucks',
    cssVars: `
      --theme-accent: #1E3932;
      --theme-accent-rgb: 30,57,50;
      --theme-accent-light: rgba(30,57,50,0.1);
      --theme-text-primary: #2d2018;
      --theme-text-secondary: #7a7067;
      --theme-text-accent: #1E3932;
      --theme-background: #f7f5f0;
      --theme-card-bg: #ffffff;
      --theme-border: #e8e2da;
      --theme-shadow: 0 2px 8px rgba(45,32,24,0.1);
      --theme-shadow-card: 0 4px 16px rgba(45,32,24,0.12);
      --theme-radius-card: 16px;
      --theme-radius-btn: 12px;
      --theme-icon-color: #2d2018;
      --theme-duration-micro: 150ms;
      --theme-ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
    `,
    background: '#f7f5f0',
    cardBg: '#ffffff',
    textPrimary: '#2d2018',
    textSecondary: '#7a7067',
    textAccent: '#1E3932',
    border: '#e8e2da',
    shadow: '0 2px 8px rgba(45,32,24,0.1)',
    shadowCard: '0 4px 16px rgba(45,32,24,0.12)',
    radiusCard: '16px',
    radiusBtn: '12px',
    accentColor: '#1E3932',
  }
}

/**
 * 获取主题对象（包含 cssVars + 扁平颜色）
 */
function getTheme(themeId) {
  return themes[themeId] || themes.apple
}

/**
 * 获取所有主题列表（用于主题选择器）
 */
function getAllThemes() {
  return Object.values(themes).map(t => ({ id: t.id, name: t.name }))
}

/**
 * 从 cssVars 字符串中提取 key-value 映射
 * @param {string} themeId
 * @returns {object} { varName: value } 不含 --theme- 前缀
 */
function injectThemeVars(themeId) {
  const theme = getTheme(themeId)
  const css = theme.cssVars
  const result = {}
  const matches = css.matchAll(/--([\w-]+):\s*([^;]+);/g)
  for (const match of matches) {
    result[match[1]] = match[2].trim()
  }
  return result
}

module.exports = {
  themes,
  getTheme,
  getAllThemes,
  injectThemeVars
}
