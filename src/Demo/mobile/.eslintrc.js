module.exports = {
  root: true,
  parser: '@typescript-eslint/parser', // TypeScript 解析器
  parserOptions: {
    ecmaFeatures: {
      jsx: true, // 允许解析 JSX
    },
    ecmaVersion: 2018, // ES9/ES2018
    sourceType: 'module', // ECMAScript 模块
  },
  extends: [
    'eslint:recommended', // ESLint 官方推荐规则
    'plugin:@typescript-eslint/recommended', // TypeScript 插件推荐规则
  ],
  rules: {
    semi: 'off', // 不强制使用分号
    'no-unused-vars': 'warn', // 未使用变量警告
    'no-unreachable': 'warn', // 代码无法到达警告
    'no-constant-condition': 'warn', // 常量作为条件警告
    'no-return-await': 'warn', // 不必要的 return await 警告
    'no-console': 'warn', // 控制台语句警告
    'comma-dangle': 'off', // 逗号结尾可以忽略（prettier 会处理）
  },
  env: {
    es6: true, // 支持所有 ES6 全局变量
    browser: true, // 浏览器全局变量
    node: true, // Node.js 全局变量和 Node.js 作用域
  }
};
