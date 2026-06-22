<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { OrdInput, OrdButton, useToast } from '../components/ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { show } = useToast()

const account = ref('')
const password = ref('')
const showPwd = ref(false)
const rememberMe = ref(true)
const loading = ref(false)

async function handleSubmit() {
  if (!account.value || !password.value) {
    show({ title: '请填写完整信息', variant: 'error' })
    return
  }
  loading.value = true
  try {
    await auth.login(account.value, password.value)
    show({ title: '登录验证已通过，正在进入工作台。', variant: 'success' })
    const redirect = (router.currentRoute.value.query.redirect as string) || '/dashboard'
    setTimeout(() => router.push(redirect), 520)
  } catch {
    show({ title: '用户名或密码错误', variant: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page-shell">
    <section class="auth-frame">
      <aside class="promo-panel">
        <div class="brand-row">
          <div class="brand-mark">RD</div>
          <div>
            <div class="brand-name">OpenRD</div>
            <span class="brand-caption">Rare Disease Collaboration</span>
          </div>
        </div>
        <div class="promo-copy">
          <p class="eyebrow">Build with care</p>
          <h2 class="promo-title">让每一个罕见需求，被认真看见。</h2>
          <p class="promo-desc">连接患者、开发者与产品经理，用协作任务流推动罕见病数字工具从想法走向可用。</p>
        </div>
        <div class="visual-board" aria-hidden="true">
          <div class="dashboard-card mini-card">
            <div class="card-label">This Week <span class="status-dot"></span></div>
            <strong>24</strong>
            <span>个需求完成审核，进入协作队列。</span>
          </div>
          <div class="dashboard-card floating-card">
            <div class="card-label">Team Progress <span class="status-dot"></span></div>
            <div class="progress-title">队伍招募中</div>
            <div class="progress-bar"><span></span></div>
            <div class="avatar-stack">
              <div class="avatar">FE</div>
              <div class="avatar">BE</div>
              <div class="avatar">QA</div>
            </div>
          </div>
          <div class="dashboard-card main-card">
            <div class="card-label">OpenRD Workspace <span class="status-dot"></span></div>
            <div class="metric-row">
              <div class="metric"><strong>128</strong><span>公开需求</span></div>
              <div class="metric"><strong>36</strong><span>招募任务</span></div>
              <div class="metric"><strong>412</strong><span>共建成员</span></div>
            </div>
            <div class="task-line"><i></i><span>用药提醒小程序原型优化</span><b>招募中</b></div>
            <div class="task-line"><i></i><span>疾病知识库标签整理</span><b>审核中</b></div>
            <div class="task-line"><i></i><span>患者随访表单无障碍改造</span><b>进行中</b></div>
          </div>
        </div>
      </aside>

      <section class="login-panel">
        <div class="login-card">
          <div class="login-brand">
            <div class="brand-mark">RD</div>
            <div>
              <div class="brand-name">OpenRD</div>
              <span class="brand-caption">Collaboration Platform</span>
            </div>
          </div>
          <header class="login-header">
            <p class="login-label">Welcome back</p>
            <h1>登录工作台</h1>
            <p class="login-subtitle">进入你的需求、工单与协作队伍，继续推进每一个值得被完成的项目。</p>
          </header>
          <form novalidate @submit.prevent="handleSubmit">
            <div class="form-field">
              <label for="account">邮箱 / 手机号</label>
              <OrdInput id="account" v-model="account" type="text" autocomplete="username" placeholder="name@example.com" />
            </div>
            <div class="form-field">
              <label for="password">密码</label>
              <div class="input-wrap">
                <OrdInput id="password" v-model="password" :type="showPwd ? 'text' : 'password'" autocomplete="current-password" placeholder="输入登录密码" />
                <button class="password-toggle" type="button" @click="showPwd = !showPwd">{{ showPwd ? '隐藏' : '显示' }}</button>
              </div>
            </div>
            <div class="form-options">
              <label class="remember-me">
                <input v-model="rememberMe" type="checkbox" />
                <span>记住我</span>
              </label>
              <router-link to="/forgot-password">忘记密码？</router-link>
            </div>
            <OrdButton variant="primary" size="lg" :loading="loading" class="submit-button" type="submit">
              {{ loading ? '正在登录' : '登录 OpenRD' }}
            </OrdButton>
          </form>
          <p class="signup-note">还没有账号？<router-link to="/register">申请加入共建者社区</router-link></p>
          <p class="login-hint">测试：chenbei / linzixuan / zhaoming / admin　密码：OpenRD#2026</p>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background:
    radial-gradient(circle at 14% 12%, rgba(20, 110, 245, 0.08), transparent 26%),
    radial-gradient(circle at 88% 84%, rgba(122, 61, 255, 0.08), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.auth-frame {
  width: min(1460px, 100%);
  min-height: 640px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 515px;
  overflow: hidden;
  background: var(--ord-color-white);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: 8px;
  box-shadow: var(--ord-shadow-cascade);
}

.promo-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  padding: 40px;
  background:
    linear-gradient(160deg, rgba(20, 110, 245, 0.95), rgba(0, 85, 212, 0.92) 42%, rgba(8, 8, 8, 0.96)),
    var(--ord-color-blue);
  color: var(--ord-color-white);
}

.promo-panel::before,
.promo-panel::after {
  content: "";
  position: absolute;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 50%;
  pointer-events: none;
}

.promo-panel::before {
  width: 460px;
  height: 460px;
  top: -190px;
  right: -120px;
}

.promo-panel::after {
  width: 360px;
  height: 360px;
  left: -160px;
  bottom: -180px;
}

.brand-row,
.login-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 4px;
  background: var(--ord-color-white);
  color: var(--ord-color-blue);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.login-brand .brand-mark {
  background: var(--ord-color-blue);
  color: var(--ord-color-white);
}

.brand-name {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.2px;
}

.brand-caption {
  display: block;
  margin-top: 2px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
  font-weight: 550;
  letter-spacing: 1.1px;
  text-transform: uppercase;
}

.login-brand .brand-caption {
  color: var(--ord-color-gray-300);
}

.promo-copy {
  position: relative;
  z-index: 2;
  max-width: 500px;
  margin-top: 42px;
}

.eyebrow {
  margin: 0 0 16px;
  color: rgba(255, 255, 255, 0.76);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.promo-title {
  margin: 0;
  font-size: clamp(44px, 5vw, 64px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.8px;
}

.promo-desc {
  max-width: 440px;
  margin: 20px 0 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 18px;
  font-weight: 500;
  line-height: 1.5;
}

.visual-board {
  position: relative;
  z-index: 2;
  min-height: 300px;
  margin-top: 36px;
}

.dashboard-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.96);
  color: var(--ord-color-black);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(14px);
}

.main-card {
  left: 0;
  right: 32px;
  bottom: 0;
  min-height: 230px;
  padding: 18px;
}

.floating-card {
  top: 8px;
  right: 0;
  width: 210px;
  padding: 16px;
  transform: rotate(2deg);
}

.mini-card {
  top: 42px;
  left: 24px;
  width: 168px;
  padding: 14px;
  transform: rotate(-3deg);
}

.card-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  color: var(--ord-color-gray-500);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ord-color-green);
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.metric {
  padding: 12px;
  border: 1px solid var(--ord-color-border);
  border-radius: 4px;
  background: #fff;
}

.metric strong {
  display: block;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.05;
}

.metric span {
  display: block;
  margin-top: 6px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  line-height: 1.3;
}

.task-line {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid #ececec;
  font-size: 13px;
}

.task-line i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--ord-color-blue);
  font-style: normal;
}

.task-line:nth-child(2) i {
  background: var(--ord-color-purple);
}

.task-line:nth-child(3) i {
  background: var(--ord-color-orange);
}

.task-line b {
  font-size: 11px;
  font-weight: 600;
  color: var(--ord-color-blue);
}

.progress-title {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.16;
  letter-spacing: -0.3px;
}

.progress-bar {
  height: 8px;
  margin: 16px 0 12px;
  overflow: hidden;
  border-radius: 4px;
  background: #e9efff;
}

.progress-bar span {
  display: block;
  width: 72%;
  height: 100%;
  background: linear-gradient(90deg, var(--ord-color-blue), var(--ord-color-purple));
}

.avatar-stack {
  display: flex;
  align-items: center;
  margin-top: 12px;
}

.avatar {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  margin-right: -7px;
  border: 2px solid var(--ord-color-white);
  border-radius: 50%;
  background: var(--ord-color-black);
  color: var(--ord-color-white);
  font-size: 10px;
  font-weight: 600;
}

.avatar:nth-child(2) {
  background: var(--ord-color-pink);
}

.avatar:nth-child(3) {
  background: var(--ord-color-green);
  color: var(--ord-color-black);
}

.mini-card strong {
  display: block;
  font-size: 30px;
  font-weight: 600;
  line-height: 1;
}

.mini-card span {
  display: block;
  margin-top: 8px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.4;
}

.login-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px 44px;
  background: var(--ord-color-white);
}

.login-card {
  width: min(100%, 390px);
}

.login-card .brand-name {
  color: var(--ord-color-black);
}

.login-header {
  margin: 34px 0 24px;
}

.login-label {
  margin: 0 0 12px;
  color: var(--ord-color-blue);
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: clamp(34px, 4vw, 48px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.8px;
}

.login-subtitle {
  margin: 14px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 16px;
  font-weight: 500;
  line-height: 1.6;
  letter-spacing: -0.16px;
}

.form-field {
  margin-bottom: 16px;
}

.form-field label {
  display: block;
  margin-bottom: 8px;
  color: var(--ord-color-gray-800);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.input-wrap {
  position: relative;
}

.form-field :deep(.ord-input) {
  height: 52px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.16px;
}

.input-wrap :deep(.ord-input) {
  padding-right: 64px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 10px;
  height: 32px;
  padding: 0 8px;
  color: var(--ord-color-gray-500);
  background: transparent;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  transform: translateY(-50%);
}

.password-toggle:hover {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 4px 0 24px;
  color: var(--ord-color-gray-500);
  font-size: 14px;
  line-height: 1.4;
}

.remember-me {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.remember-me input {
  width: 16px;
  height: 16px;
  accent-color: var(--ord-color-blue);
}

.form-options a,
.signup-note a {
  color: var(--ord-color-blue);
  text-decoration: none;
}

.form-options a:hover,
.signup-note a:hover {
  color: var(--ord-color-blue-hover, #0055d4);
  text-decoration: underline;
}

.submit-button {
  width: 100%;
}

.submit-button :deep(.ord-button) {
  width: 100%;
  min-height: 54px;
  font-size: 16px;
  letter-spacing: -0.16px;
}

.signup-note {
  margin: 26px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
}

.login-hint {
  margin: 16px 0 0;
  color: var(--ord-color-gray-300);
  font-size: 11px;
  text-align: center;
  line-height: 1.5;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 991px) {
  .page-shell { padding: 24px; }
  .auth-frame { min-height: 600px; grid-template-columns: 0.9fr 1fr; }
  .promo-panel { padding: 32px; }
  .promo-title { font-size: 44px; }
  .promo-desc { font-size: 16px; }
  .floating-card { width: 180px; }
  .metric-row { grid-template-columns: 1fr; }
  .metric:nth-child(3) { display: none; }
}

@media (max-width: 767px) {
  .page-shell { min-height: auto; padding: 0; background: var(--ord-color-white); }
  .auth-frame { width: 100%; min-height: 100vh; display: block; border: 0; border-radius: 0; box-shadow: none; }
  .promo-panel { min-height: 220px; padding: 24px; }
  .promo-copy { margin-top: 28px; }
  .promo-title { max-width: 420px; font-size: 38px; }
  .promo-desc { max-width: 480px; margin-top: 12px; }
  .visual-board { display: none; }
  .login-panel { min-height: calc(100vh - 220px); padding: 28px 24px; }
  .login-header { margin-top: 28px; }
}

@media (max-width: 479px) {
  .promo-panel { min-height: 196px; padding: 20px; }
  .brand-mark { width: 34px; height: 34px; }
  .brand-name { font-size: 18px; }
  .brand-caption { font-size: 10px; }
  .promo-title { font-size: 32px; }
  .promo-desc { font-size: 14px; line-height: 1.5; }
  .login-panel { min-height: calc(100vh - 196px); padding: 22px 18px; }
  .login-header { margin: 24px 0 20px; }
  h1 { font-size: 34px; }
  .form-options { align-items: flex-start; flex-direction: column; }
  .submit-button:hover { transform: translateX(0); }
}
</style>
