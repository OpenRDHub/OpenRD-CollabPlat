<template>
  <div class="workbench-view">
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

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

// 根据用户角色确定工作台类型
const activeRole = computed(() => {
  const role = auth.userRole || 'requester'
  // 将系统角色映射到工作台角色
  if (role === 'admin') return 'admin'
  if (role === 'operator') return 'operator'
  if (role === 'builder') return 'builder'
  return 'requester' // 默认为需求者
})

// 角色数据配置
const roleData: Record<string, any> = {
  operator: {
    title: '运营管理员工作台',
    description: '关注需求沟通、边界判断和任务转化，管理类配置由超级管理员维护。',
    tileSummary: '运管 / 产品经理仅处理自己的需求沟通与转化，不进入全量任务管理或需求管理。',
    metrics: [
      {
        title: '待沟通需求',
        value: '2',
        note: '仅展示当前运管自己的会话',
        tone: 'rgba(20, 110, 245, 0.1)',
      },
      {
        title: '可转化需求',
        value: '1',
        note: '信息充分，可生成任务工单',
        tone: 'rgba(0, 215, 34, 0.12)',
      },
      {
        title: '已转化追踪',
        value: '0',
        note: '转化后进入任务详情查看',
        tone: 'rgba(255, 174, 19, 0.16)',
      },
    ],
    tiles: ['profile', 'messageCenter', 'demandCommunication', 'myTasks', 'myDemands'],
  },
  builder: {
    title: '共建者工作台',
    description: '浏览任务大厅、申请加入队伍、协作开发并交付成果。',
    tileSummary: '共建者可以浏览任务、申请加入、查看自己参与的任务进度。',
    metrics: [
      {
        title: '可申请任务',
        value: '8',
        note: '任务大厅公开招募中',
        tone: 'rgba(20, 110, 245, 0.1)',
      },
      {
        title: '进行中任务',
        value: '3',
        note: '我参与的开发任务',
        tone: 'rgba(255, 107, 0, 0.12)',
      },
      {
        title: '已完成任务',
        value: '12',
        note: '累计交付成果',
        tone: 'rgba(0, 215, 34, 0.12)',
      },
    ],
    tiles: ['taskHall', 'myTasks', 'teamWork', 'profile', 'messageCenter'],
  },
  requester: {
    title: '需求者工作台',
    description: '提交需求、查看需求状态、与运管沟通并跟踪任务进展。',
    tileSummary: '需求者可以提交新需求、查看自己的需求状态和反馈。',
    metrics: [
      {
        title: '待审核需求',
        value: '1',
        note: '等待运管审核处理',
        tone: 'rgba(255, 174, 19, 0.16)',
      },
      {
        title: '沟通中需求',
        value: '2',
        note: '运管正在补齐信息',
        tone: 'rgba(122, 61, 255, 0.1)',
      },
      {
        title: '已转化任务',
        value: '5',
        note: '需求已生成任务工单',
        tone: 'rgba(0, 215, 34, 0.12)',
      },
    ],
    tiles: ['submitDemand', 'myDemands', 'demandDetail', 'profile', 'messageCenter'],
  },
  admin: {
    title: '超级管理员工作台',
    description: '全局管理用户、权限、需求、任务和系统配置。',
    tileSummary: '超管拥有完整的系统管理权限，可以查看和操作所有功能模块。',
    metrics: [
      {
        title: '总用户数',
        value: '248',
        note: '平台注册用户',
        tone: 'rgba(20, 110, 245, 0.1)',
      },
      {
        title: '总需求数',
        value: '156',
        note: '所有需求记录',
        tone: 'rgba(122, 61, 255, 0.1)',
      },
      {
        title: '总任务数',
        value: '89',
        note: '所有任务记录',
        tone: 'rgba(255, 107, 0, 0.12)',
      },
      {
        title: '活跃队伍',
        value: '32',
        note: '进行中的协作队伍',
        tone: 'rgba(0, 215, 34, 0.12)',
      },
    ],
    tiles: [
      'userManagement',
      'demandManagement',
      'taskManagement',
      'systemLogs',
      'profile',
      'messageCenter',
    ],
  },
}

// 功能卡片目录
const tileCatalog: Record<string, any> = {
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
  demandCommunication: {
    title: '需求沟通',
    desc: '进入自己负责的需求会话，补齐边界后转化任务。',
    badge: 'Talk',
    icon: 'C',
    color: '#ff6b00',
    bg: 'rgba(255, 107, 0, 0.12)',
    route: '/demands/REQ-2418',
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
  taskHall: {
    title: '任务大厅',
    desc: '浏览公开招募的任务，申请加入感兴趣的队伍。',
    badge: 'Hall',
    icon: 'H',
    color: '#146ef5',
    bg: 'rgba(20, 110, 245, 0.1)',
    route: '/hall',
  },
  teamWork: {
    title: '队伍协作',
    desc: '与队友协同开发，查看任务进度和交付物。',
    badge: 'Team',
    icon: 'T',
    color: '#ff6b00',
    bg: 'rgba(255, 107, 0, 0.12)',
    route: '/teams',
  },
  submitDemand: {
    title: '提交需求',
    desc: '描述你的问题，上传相关材料并提交审核。',
    badge: 'New',
    icon: '+',
    color: '#00a91b',
    bg: 'rgba(0, 215, 34, 0.12)',
    route: '/hall', // 会触发提需求弹窗
  },
  demandDetail: {
    title: '需求详情',
    desc: '查看需求沟通记录和平台反馈。',
    badge: 'View',
    icon: 'D',
    color: '#7a3dff',
    bg: 'rgba(122, 61, 255, 0.1)',
    route: '/demands/REQ-2418',
  },
  userManagement: {
    title: '用户管理',
    desc: '管理平台用户、角色权限和账号状态。',
    badge: 'Admin',
    icon: 'U',
    color: '#146ef5',
    bg: 'rgba(20, 110, 245, 0.1)',
    route: '/admin/users',
  },
  demandManagement: {
    title: '需求管理',
    desc: '审核、沟通并转化全量需求，维护转化状态。',
    badge: 'Admin',
    icon: 'D',
    color: '#ff6b00',
    bg: 'rgba(255, 107, 0, 0.12)',
    route: '/admin/demand-management',
  },
  taskManagement: {
    title: '任务管理',
    desc: '管理所有任务的状态、队伍和交付进度。',
    badge: 'Admin',
    icon: 'T',
    color: '#7a3dff',
    bg: 'rgba(122, 61, 255, 0.1)',
    route: '/admin/tasks',
  },
  systemLogs: {
    title: '系统日志',
    desc: '查看关键操作审计日志和系统事件。',
    badge: 'Admin',
    icon: 'L',
    color: '#5a5a5a',
    bg: 'rgba(90, 90, 90, 0.12)',
    route: '/admin/logs',
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
  padding: 0;
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
