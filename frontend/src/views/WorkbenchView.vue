<template>
  <div class="workbench-view">
    <TopNavbar />
    <div class="workbench-frame">
      <!-- 背景装饰元素 -->
      <div class="ambient-ring"></div>
      <div class="ambient-node"></div>

      <!-- Hero 卡片 -->
      <section class="hero-card">
        <div>
          <p class="section-label">Workbench</p>
          <h1>{{ currentRole.title }}</h1>
          <p class="hero-copy">{{ currentRole.description }}</p>
        </div>
      </section>

      <!-- 信息区 - 统计卡片 -->
      <section class="info-section" aria-label="信息区">
        <div class="info-grid">
          <article
            v-for="(metric, index) in currentRole.metrics"
            :key="index"
            class="info-card"
            :style="{ '--tone': metric.tone }"
          >
            <span class="info-value">{{ metric.value }}</span>
            <span class="info-title">{{ metric.title }}</span>
            <span class="info-note">{{ metric.note }}</span>
          </article>
        </div>
      </section>

      <!-- 功能区 - 功能卡片 -->
      <section class="tile-section" aria-label="功能区">
        <div class="section-heading">
          <div>
            <p class="section-label">Function Tiles</p>
            <h2>功能区</h2>
          </div>
          <p class="tile-summary">{{ currentRole.tileSummary }}</p>
        </div>
        <div class="tile-grid">
          <article
            v-for="tileKey in currentRole.tiles"
            :key="tileKey"
            class="tile-card"
            @click="navigateTo(tileCatalog[tileKey])"
          >
            <div class="tile-top">
              <span
                class="tile-icon"
                :style="{
                  '--icon-color': tileCatalog[tileKey].color,
                  '--icon-bg': tileCatalog[tileKey].bg,
                }"
              >
                {{ tileCatalog[tileKey].icon }}
              </span>
              <span class="tile-badge">{{ tileCatalog[tileKey].badge }}</span>
            </div>
            <div>
              <h3 class="tile-title">{{ tileCatalog[tileKey].title }}</h3>
              <p class="tile-desc">{{ tileCatalog[tileKey].desc }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/components/ui/toast/useToast'
import TopNavbar from '@/components/TopNavbar.vue'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

// 根据用户角色确定工作台类型
const activeRole = computed(() => {
  const role = auth.userRole || 'requester'
  if (role === 'super_admin') return 'super_admin'
  if (role === 'operator') return 'operator'
  if (role === 'builder') return 'builder'
  return 'requester'
})

// 角色数据配置（严格对齐 demo/all-pages/workbench.html）
const roleData: Record<string, any> = {
  requester: {
    title: '需求者工作台',
    description: '聚焦你提交的需求进度，快速查看审核、转化与参与工单状态。',
    tileSummary: '需求者仅展示与自身需求相关的功能入口。',
    metrics: [
      { title: '我的需求总数', value: '12', note: '其中待审核 3 个', tone: 'rgba(20, 110, 245, 0.1)' },
      { title: '已转化的需求数', value: '5', note: '已进入开发流程', tone: 'rgba(0, 215, 34, 0.12)' },
      { title: '平台累计完成工单数', value: '74', note: '仅展示，增强协作信心', tone: 'rgba(255, 174, 19, 0.16)' },
      { title: '我参与的工单数', value: '3', note: '进行中 1 / 已完成 2', tone: 'rgba(122, 61, 255, 0.1)' },
    ],
    tiles: ['profile', 'messageCenter', 'myDemands'],
  },
  builder: {
    title: '共建者工作台',
    description: '快速处理自己参与的任务、队伍申请与需要关注的需求。',
    tileSummary: '共建者功能区聚焦个人任务和个人需求。',
    metrics: [
      { title: '我是队长的工单数', value: '4', note: '2 个正在招募成员', tone: 'rgba(20, 110, 245, 0.1)' },
      { title: '待我处理的申请数', value: '7', note: '队长专用，来自成员加入申请', tone: 'rgba(255, 174, 19, 0.16)' },
      { title: '待审核需求数', value: '9', note: '高亮提醒，需紧急处理', tone: 'rgba(238, 29, 54, 0.1)' },
    ],
    tiles: ['profile', 'messageCenter', 'myTasks', 'myDemands'],
  },
  operator: {
    title: '产品经理工作台',
    description: '关注需求审核、任务流转和平台整体协作效率。',
    tileSummary: '产品经理可管理任务和需求，也保留个人任务/需求入口。',
    metrics: [
      { title: '本月转化率', value: '62%', note: '已转化需求 / 总审核数', tone: 'rgba(0, 215, 34, 0.12)' },
      { title: '全部进行中工单数', value: '36', note: '含招募、开发、验收阶段', tone: 'rgba(20, 110, 245, 0.1)' },
      { title: '平台总注册用户数', value: '680', note: '患者/家属 268 · 志愿者 412', tone: 'rgba(122, 61, 255, 0.1)' },
    ],
    tiles: ['profile', 'messageCenter', 'taskManage', 'demandManage', 'myTasks', 'myDemands'],
  },
  super_admin: {
    title: '超级管理员工作台',
    description: '面向全局治理、权限配置、审计追踪和核心平台指标。',
    tileSummary: '超级管理员可访问全部核心管理入口。',
    metrics: [
      { title: '今日活跃用户数', value: '148', note: 'DAU，较昨日 +12%', tone: 'rgba(20, 110, 245, 0.1)' },
      { title: '近 7 天新增需求数', value: '31', note: '含待审核与已转化需求', tone: 'rgba(255, 174, 19, 0.16)' },
      { title: '近 7 天新增工单数', value: '18', note: '由需求转化和官方创建组成', tone: 'rgba(0, 215, 34, 0.12)' },
    ],
    tiles: ['profile', 'messageCenter', 'userManage', 'permissionManage', 'systemLog', 'taskManage', 'demandManage', 'myTasks', 'myDemands'],
  },
}

// 功能卡片目录（严格对齐 demo/all-pages/workbench.html）
const tileCatalog: Record<string, any> = {
  userManage: {
    title: '用户管理',
    desc: '查看、禁用、重置用户状态。',
    badge: 'Admin',
    icon: 'U',
    color: '#146ef5',
    bg: 'rgba(20, 110, 245, 0.1)',
    route: '/admin/user-management',
  },
  permissionManage: {
    title: '权限管理',
    desc: '配置角色权限与菜单访问范围。',
    badge: 'Role',
    icon: 'P',
    color: '#7a3dff',
    bg: 'rgba(122, 61, 255, 0.1)',
    route: '/admin/permission-management',
  },
  systemLog: {
    title: '系统日志',
    desc: '审计敏感操作和异常行为。',
    badge: 'Log',
    icon: 'L',
    color: '#ee1d36',
    bg: 'rgba(238, 29, 54, 0.1)',
    route: '/admin/system-logs',
  },
  profile: {
    title: '个人信息',
    desc: '查看并维护头像、手机号、职业与擅长领域。',
    badge: 'Me',
    icon: 'I',
    color: '#146ef5',
    bg: 'rgba(20, 110, 245, 0.1)',
    route: '/profile',
  },
  messageCenter: {
    title: '消息中心',
    desc: '查看系统通知、任务进度、需求反馈和队伍申请。',
    badge: 'Msg',
    icon: 'N',
    color: '#7a3dff',
    bg: 'rgba(122, 61, 255, 0.1)',
    route: '/messages',
  },
  taskManage: {
    title: '任务管理',
    desc: '管理全量任务、状态与关闭操作。',
    badge: 'Task',
    icon: 'T',
    color: '#ff6b00',
    bg: 'rgba(255, 107, 0, 0.1)',
    route: '/admin/task-management',
  },
  demandManage: {
    title: '需求管理',
    desc: '审核、编辑并转化用户需求。',
    badge: 'Need',
    icon: 'D',
    color: '#ffae13',
    bg: 'rgba(255, 174, 19, 0.16)',
    route: '/admin/demand-management',
  },
  myTasks: {
    title: '我的任务',
    desc: '查看我参与、负责或待处理的任务。',
    badge: 'Mine',
    icon: 'M',
    color: '#00a91b',
    bg: 'rgba(0, 215, 34, 0.12)',
    route: '/my-tasks',
  },
  myDemands: {
    title: '我的需求',
    desc: '查看我提交的需求与当前状态。',
    badge: 'Self',
    icon: 'R',
    color: '#ed52cb',
    bg: 'rgba(237, 82, 203, 0.1)',
    route: '/my-demands',
  },
}

// 当前角色数据
const currentRole = computed(() => {
  return roleData[activeRole.value] || roleData.requester
})

// 导航到功能页面
function navigateTo(tile: any) {
  toast.show({
    title: '已进入',
    description: tile.title,
    variant: 'default',
  })

  setTimeout(() => {
    router.push(tile.route)
  }, 260)
}
</script>

<style scoped>
.workbench-view {
  min-height: calc(100vh - 76px);
  padding: 96px 32px 32px;
}

.workbench-frame {
  position: relative;
  width: min(1460px, 100%);
  margin: 0 auto;
  padding: 32px;
}

/* 背景装饰 */
.ambient-ring,
.ambient-node {
  position: absolute;
  pointer-events: none;
  z-index: -1;
}

.ambient-ring {
  width: 280px;
  height: 280px;
  right: -70px;
  top: 92px;
  border: 1px solid rgba(20, 110, 245, 0.1);
  border-radius: 50%;
}

.ambient-node {
  width: 140px;
  height: 70px;
  left: -48px;
  bottom: 84px;
  background: radial-gradient(circle at 8px 14px, rgba(20, 110, 245, 0.22) 0 4px, transparent 5px),
    radial-gradient(circle at 72px 38px, rgba(0, 215, 34, 0.18) 0 5px, transparent 6px),
    radial-gradient(circle at 128px 16px, rgba(237, 82, 203, 0.18) 0 4px, transparent 5px),
    linear-gradient(18deg, transparent 0 16px, rgba(20, 110, 245, 0.08) 17px 18px, transparent 19px 100%);
}

/* Hero 卡片 */
.hero-card {
  display: block;
  padding: 24px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.section-label {
  margin: 0 0 10px;
  color: var(--ord-color-blue-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  line-height: 1.3;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: clamp(40px, 5vw, 58px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.8px;
}

.hero-copy {
  max-width: 720px;
  margin: 14px 0 0;
  color: var(--ord-color-gray-600);
  font-size: 16px;
  line-height: 1.58;
}

/* 信息区 */
.info-section {
  margin-top: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.info-card {
  position: relative;
  min-height: 132px;
  overflow: hidden;
  padding: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.info-card::after {
  content: '';
  position: absolute;
  width: 104px;
  height: 104px;
  right: -42px;
  top: -48px;
  border-radius: 50%;
  background: var(--tone, rgba(20, 110, 245, 0.1));
}

.info-value {
  position: relative;
  z-index: 1;
  display: block;
  color: var(--ord-color-black);
  font-size: 40px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.8px;
}

.info-title {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 12px;
  color: var(--ord-color-gray-800);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.info-note {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 12px;
  color: var(--ord-color-gray-600);
  font-size: 13px;
  line-height: 1.45;
}

/* 功能区 */
.tile-section {
  margin-top: 18px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
}

.section-heading h2 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 32px;
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: -0.5px;
}

.tile-summary {
  max-width: 460px;
  margin: 0;
  color: var(--ord-color-gray-600);
  font-size: 14px;
  line-height: 1.55;
  text-align: right;
}

.tile-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.tile-card {
  min-height: 164px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
  cursor: pointer;
  transition: transform var(--ord-transition-base), border-color var(--ord-transition-base),
    box-shadow var(--ord-transition-base);
}

.tile-card:hover {
  border-color: var(--ord-color-blue-600);
  box-shadow: 0 18px 36px rgba(20, 110, 245, 0.14);
  transform: translateX(6px);
}

.tile-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.tile-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  color: var(--icon-color, var(--ord-color-blue-600));
  background: var(--icon-bg, rgba(20, 110, 245, 0.1));
  border-radius: var(--ord-radius-sm);
  font-size: 18px;
  font-weight: 800;
}

.tile-badge {
  min-height: 26px;
  display: inline-flex;
  align-items: center;
  padding: 0 9px;
  color: var(--ord-color-blue-600);
  background: rgba(20, 110, 245, 0.08);
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.tile-title {
  margin: 20px 0 0;
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.25;
}

.tile-desc {
  margin: 8px 0 0;
  color: var(--ord-color-gray-600);
  font-size: 14px;
  line-height: 1.5;
}

/* 响应式 */
@media (max-width: 1100px) {
  .info-grid,
  .tile-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .workbench-frame {
    padding: 22px 16px;
  }

  .hero-card,
  .info-grid,
  .tile-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    padding: 22px;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .tile-summary {
    text-align: left;
  }

  .ambient-ring,
  .ambient-node {
    display: none;
  }
}

@media (max-width: 520px) {
  h1 {
    font-size: 36px;
  }

  .section-heading h2 {
    font-size: 28px;
  }
}
</style>
