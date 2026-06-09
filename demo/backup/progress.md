# OpenRD Demo Progress

## 当前项目认知

- 项目目录：`E:\MyCode\OpenRD\demo`
- 技术栈：纯 `HTML + CSS + JS`
- 当前无构建工具、无框架、无 `package.json`
- 页面主要采用单文件结构：每个 HTML 内联 `<style>` 与 `<script>`
- 当前目标：生成可供绘制高保真原型图参考的 Webflow 风格 demo

## 已有页面

- `login.html`：OpenRD 登录页
- `register.html`：OpenRD 注册页
- `forgot-password.html`：忘记密码 / 重置密码流程
- `account-onboarding.html`：账号初始化流程
- `account-onboarding copy.html`：账号初始化页面副本或旧版本
- `gesture-particles/index.html`：摄像头手势识别 + Canvas 粒子互动 demo
- `gesture-particles/README.md`：手势粒子 demo 使用说明

## 设计系统约束

当前项目遵循 Webflow 风格设计系统：

- 背景：白色 `#ffffff`
- 主文本：近黑 `#080808`
- 主 CTA：Webflow Blue `#146ef5`
- Hover Blue：`#0055d4`
- 边框：`#d8d8d8`
- Hover 边框：`#898989`
- 辅助色：
  - Purple `#7a3dff`
  - Pink `#ed52cb`
  - Green `#00d722`
  - Orange `#ff6b00`
  - Yellow `#ffae13`
  - Red `#ee1d36`
- 圆角：以 `4px`、`8px` 为主，避免过圆
- 阴影：使用 5 层 cascading shadow
- 字体：优先 `WF Visual Sans Variable`，fallback `Arial`
- 标签：uppercase，小字号，较大 letter-spacing
- 按钮 hover：优先使用 `translateX(6px)` 或类似轻量位移动效

## 已识别交互模式

- 登录页：
  - 密码显示/隐藏
  - 提交 loading
  - 模拟登录成功提示
- 注册页：
  - 验证码倒计时
  - 密码显示/隐藏
  - 必填校验
  - 模拟注册成功提示
- 忘记密码页：
  - 两步流程
  - 验证码倒计时
  - 新密码校验
  - 模拟重置成功提示
- 账号初始化页：
  - 多步骤切换
  - 身份选择
  - 岗位多选
  - 疾病方向分支
  - 自定义标签添加/删除
  - 简介字数统计
- 手势粒子页：
  - MediaPipe 手势识别
  - Canvas 粒子特效
  - 鼠标模拟模式

## 后续开发原则

- 继续使用纯 `HTML + CSS + JS`
- 新 demo 页面默认保持单文件 HTML，除非明确要求拆分
- 不引入框架或构建工具，除非明确要求
- 优先保证视觉完整度、信息层级和原型可读性
- 表单和流程可以使用模拟数据与前端状态，不接真实后端
- 视觉需贴近 Webflow：干净白底、锐利卡片、强 typography、蓝色 CTA、多彩辅助状态
- 修改时应尽量复用已有 CSS 变量、卡片样式、按钮行为和文案语境

## 推荐下一步页面方向

- 首页工作台 / Dashboard
- 需求广场 / Request Marketplace
- 需求详情页 / Request Detail
- 任务招募页 / Task Recruiting
- 患者需求发布页 / Submit Request
- 成员个人主页 / Member Profile
- 项目协作空间 / Project Workspace
- 消息通知中心 / Notifications

## 恢复上下文提示

如果之后重新启动 Codex CLI，可以优先使用：

```bash
codex resume
```

如果没有恢复到本会话，也可以让新的模型先阅读本文件：

```text
请先阅读 progress.md，了解当前 OpenRD demo 项目状态，然后继续开发。
```

