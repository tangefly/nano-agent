/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'media',   // ← 这一行最重要！使用 prefers-color-scheme 自动适配系统
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    // 其他路径根据你的项目结构添加
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}