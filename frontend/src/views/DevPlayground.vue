<script setup lang="ts">
import { ref } from 'vue'
import {
  OrdButton,
  OrdInput,
  OrdTextarea,
  OrdCard,
  OrdCardHeader,
  OrdCardContent,
  OrdBadge,
  OrdTable,
  OrdTableHeader,
  OrdTableRow,
  OrdTableCell,
  OrdDialog,
  OrdTabs,
  OrdTabsList,
  OrdTabsTrigger,
  OrdTabsContent,
  OrdDropdown,
  OrdDropdownItem,
  OrdSelect,
  OrdTooltip,
  OrdPagination,
  OrdNavbar,
  OrdSidebar,
  OrdAvatar,
  OrdProgress,
  OrdTimeline,
  OrdFileUpload,
  OrdEmptyState,
  OrdSearchBox,
  useToast,
} from '../components/ui'

const inputVal = ref('')
const textareaVal = ref('')
const dialogOpen = ref(false)
const selectVal = ref('')
const currentPage = ref(1)
const searchVal = ref('')
const uploadedFiles = ref<File[]>([])

const { show: showToast } = useToast()

const selectOptions = [
  { value: 'vue', label: 'Vue' },
  { value: 'react', label: 'React' },
  { value: 'angular', label: 'Angular' },
]

const sidebarItems = [
  { label: '仪表盘', icon: '📊', active: true },
  { label: '需求管理', icon: '📋' },
  { label: '任务管理', icon: '✅' },
  { label: '团队', icon: '👥' },
  { label: '设置', icon: '⚙️' },
]

const timelineItems = [
  { title: '需求提交', status: 'done' as const, description: '需求者提交了新需求', date: '2026-06-01' },
  { title: '需求评审', status: 'done' as const, description: '产品经理完成评审', date: '2026-06-03' },
  { title: '任务转化', status: 'active' as const, description: '正在拆分子任务', date: '2026-06-08' },
  { title: '开发中', status: 'pending' as const, date: '待定' },
  { title: '验收交付', status: 'pending' as const },
]
</script>

<template>
  <div class="dev-playground">
    <h1>OpenRD UI - Dev Playground</h1>
    <p class="subtitle">组件库预览 — 共 20 个组件</p>

    <!-- Button -->
    <section class="section">
      <h2>OrdButton</h2>
      <div class="row">
        <OrdButton variant="primary">Primary</OrdButton>
        <OrdButton variant="ghost">Ghost</OrdButton>
        <OrdButton variant="outline">Outline</OrdButton>
        <OrdButton variant="primary" size="sm">Small</OrdButton>
        <OrdButton variant="primary" size="lg">Large</OrdButton>
        <OrdButton variant="primary" :loading="true">Loading</OrdButton>
        <OrdButton variant="primary" disabled>Disabled</OrdButton>
      </div>
    </section>

    <!-- Input -->
    <section class="section">
      <h2>OrdInput / OrdTextarea</h2>
      <div class="grid-2">
        <OrdInput v-model="inputVal" placeholder="请输入内容..." />
        <OrdInput v-model="inputVal" placeholder="错误状态" error />
        <OrdInput v-model="inputVal" placeholder="禁用" disabled />
        <OrdInput v-model="inputVal" type="password" placeholder="密码" />
      </div>
      <OrdTextarea v-model="textareaVal" placeholder="多行文本输入..." />
    </section>

    <!-- Badge -->
    <section class="section">
      <h2>OrdBadge</h2>
      <div class="row">
        <OrdBadge variant="blue">进行中</OrdBadge>
        <OrdBadge variant="green">已完成</OrdBadge>
        <OrdBadge variant="orange">待审核</OrdBadge>
        <OrdBadge variant="purple">已分配</OrdBadge>
        <OrdBadge variant="pink">紧急</OrdBadge>
        <OrdBadge variant="red">已拒绝</OrdBadge>
        <OrdBadge variant="gray">已关闭</OrdBadge>
      </div>
    </section>

    <!-- Card -->
    <section class="section">
      <h2>OrdCard</h2>
      <OrdCard>
        <OrdCardHeader>卡片标题</OrdCardHeader>
        <OrdCardContent>这是卡片内容区域，支持任意插槽内容。</OrdCardContent>
      </OrdCard>
    </section>

    <!-- Table -->
    <section class="section">
      <h2>OrdTable</h2>
      <OrdTable>
        <OrdTableHeader>
          <OrdTableCell header>名称</OrdTableCell>
          <OrdTableCell header>状态</OrdTableCell>
          <OrdTableCell header>日期</OrdTableCell>
        </OrdTableHeader>
        <OrdTableRow>
          <OrdTableCell>AI 模型训练平台</OrdTableCell>
          <OrdTableCell>
            <OrdBadge variant="blue">进行中</OrdBadge>
          </OrdTableCell>
          <OrdTableCell>2026-06-10</OrdTableCell>
        </OrdTableRow>
        <OrdTableRow>
          <OrdTableCell>数据标注工具</OrdTableCell>
          <OrdTableCell>
            <OrdBadge variant="green">已完成</OrdBadge>
          </OrdTableCell>
          <OrdTableCell>2026-06-08</OrdTableCell>
        </OrdTableRow>
      </OrdTable>
    </section>

    <!-- Dialog -->
    <section class="section">
      <h2>OrdDialog</h2>
      <OrdButton @click="dialogOpen = true">打开对话框</OrdButton>
      <OrdDialog v-model:open="dialogOpen" title="确认操作" description="确定要提交这个需求吗？">
        <p>对话框内容区域</p>
        <template #footer>
          <OrdButton variant="ghost" @click="dialogOpen = false">取消</OrdButton>
          <OrdButton @click="dialogOpen = false">确认</OrdButton>
        </template>
      </OrdDialog>
    </section>

    <!-- Tabs -->
    <section class="section">
      <h2>OrdTabs</h2>
      <OrdTabs default-value="tab1">
        <OrdTabsList>
          <OrdTabsTrigger value="tab1">概览</OrdTabsTrigger>
          <OrdTabsTrigger value="tab2">详情</OrdTabsTrigger>
          <OrdTabsTrigger value="tab3">日志</OrdTabsTrigger>
        </OrdTabsList>
        <OrdTabsContent value="tab1">概览内容区域</OrdTabsContent>
        <OrdTabsContent value="tab2">详情内容区域</OrdTabsContent>
        <OrdTabsContent value="tab3">日志内容区域</OrdTabsContent>
      </OrdTabs>
    </section>

    <!-- Select -->
    <section class="section">
      <h2>OrdSelect</h2>
      <div class="grid-2">
        <OrdSelect v-model="selectVal" :options="selectOptions" placeholder="选择框架" />
      </div>
      <p style="margin-top: 8px; font-size: 13px; color: var(--ord-color-gray-500)">选中值: {{ selectVal || '无' }}</p>
    </section>

    <!-- Pagination -->
    <section class="section">
      <h2>OrdPagination</h2>
      <OrdPagination v-model:current-page="currentPage" :total="95" :page-size="10" />
      <p style="margin-top: 8px; font-size: 13px; color: var(--ord-color-gray-500)">当前页: {{ currentPage }}</p>
    </section>

    <!-- Avatar -->
    <section class="section">
      <h2>OrdAvatar</h2>
      <div class="row">
        <OrdAvatar name="张三" size="sm" />
        <OrdAvatar name="李明华" size="md" />
        <OrdAvatar name="王五" size="lg" />
      </div>
    </section>

    <!-- Progress -->
    <section class="section">
      <h2>OrdProgress</h2>
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <OrdProgress :value="30" />
        <OrdProgress :value="68" variant="gradient" />
        <OrdProgress :value="100" />
      </div>
    </section>

    <!-- SearchBox -->
    <section class="section">
      <h2>OrdSearchBox</h2>
      <OrdSearchBox v-model="searchVal" placeholder="搜索需求..." />
    </section>

    <!-- EmptyState -->
    <section class="section">
      <h2>OrdEmptyState</h2>
      <OrdCard>
        <OrdCardContent>
          <OrdEmptyState>
            <template #title>暂无数据</template>
            <template #description>还没有任何需求记录，点击下方按钮创建第一个需求</template>
            <template #action>
              <OrdButton size="sm">创建需求</OrdButton>
            </template>
          </OrdEmptyState>
        </OrdCardContent>
      </OrdCard>
    </section>

    <!-- Dropdown -->
    <section class="section">
      <h2>OrdDropdown</h2>
      <OrdDropdown>
        <template #trigger>
          <OrdButton variant="ghost">操作菜单 ▾</OrdButton>
        </template>
        <OrdDropdownItem>编辑项目</OrdDropdownItem>
        <OrdDropdownItem>分配任务</OrdDropdownItem>
        <OrdDropdownItem>查看日志</OrdDropdownItem>
      </OrdDropdown>
    </section>

    <!-- Toast -->
    <section class="section">
      <h2>OrdToast (useToast)</h2>
      <div class="row">
        <OrdButton variant="primary" size="sm"
          @click="showToast({ title: '操作成功', description: '需求已提交', variant: 'success' })">Success Toast</OrdButton>
        <OrdButton variant="outline" size="sm"
          @click="showToast({ title: '操作失败', description: '网络连接异常', variant: 'error' })">Error Toast</OrdButton>
        <OrdButton variant="ghost" size="sm" @click="showToast({ title: '提示', description: '这是一条普通通知' })">Default Toast
        </OrdButton>
      </div>
    </section>

    <!-- Tooltip -->
    <section class="section">
      <h2>OrdTooltip</h2>
      <div class="row">
        <OrdTooltip content="这是顶部提示" side="top">
          <OrdButton variant="ghost" size="sm">Top</OrdButton>
        </OrdTooltip>
        <OrdTooltip content="这是底部提示" side="bottom">
          <OrdButton variant="ghost" size="sm">Bottom</OrdButton>
        </OrdTooltip>
        <OrdTooltip content="这是右侧提示" side="right">
          <OrdButton variant="ghost" size="sm">Right</OrdButton>
        </OrdTooltip>
      </div>
    </section>

    <!-- Navbar -->
    <section class="section">
      <h2>OrdNavbar</h2>
      <p class="hint">Navbar 为 fixed 定位组件，此处展示其结构（见页面顶部实际效果）。</p>
      <div class="navbar-demo">
        <OrdNavbar>
          <template #brand>
            <span class="brand-text">OpenRD</span>
          </template>
          <template #actions>
            <OrdButton size="sm" variant="ghost">工作台</OrdButton>
            <OrdButton size="sm">提需求</OrdButton>
          </template>
        </OrdNavbar>
      </div>
    </section>

    <!-- Sidebar -->
    <section class="section">
      <h2>OrdSidebar</h2>
      <div style="max-width: 240px;">
        <OrdCard>
          <OrdSidebar :items="sidebarItems" />
        </OrdCard>
      </div>
    </section>

    <!-- Timeline -->
    <section class="section">
      <h2>OrdTimeline</h2>
      <OrdCard>
        <OrdCardContent>
          <OrdTimeline :items="timelineItems" />
        </OrdCardContent>
      </OrdCard>
    </section>

    <!-- FileUpload -->
    <section class="section">
      <h2>OrdFileUpload</h2>
      <OrdFileUpload v-model="uploadedFiles" accept=".pdf,.doc,.docx,.png" multiple />
    </section>
  </div>
</template>

<style scoped>
.dev-playground {
  max-width: var(--ord-content-max-width);
  margin: 0 auto;
  padding: var(--ord-space-10) var(--ord-space-8);
}

.dev-playground h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: var(--ord-space-2);
}

.subtitle {
  color: var(--ord-color-gray-500);
  margin-bottom: var(--ord-space-10);
}

.section {
  margin-bottom: var(--ord-space-10);
}

.section h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: var(--ord-space-4);
  padding-bottom: var(--ord-space-2);
  border-bottom: 1px solid var(--ord-color-border);
}

.row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--ord-space-3);
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--ord-space-3);
  margin-bottom: var(--ord-space-3);
}

.hint {
  font-size: 13px;
  color: var(--ord-color-gray-500);
  margin-bottom: var(--ord-space-3);
}

.navbar-demo {
  position: relative;
  height: 76px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  overflow: hidden;
}

.navbar-demo :deep(.ord-navbar) {
  position: absolute;
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
}
</style>
