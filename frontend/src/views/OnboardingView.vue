<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { OrdButton, useToast } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { show } = useToast()

const currentStep = ref(1)
const loading = ref(false)
const identity = ref('患者')
const selectedDiseases = ref<string[]>(['罕见神经肌肉病'])
const selectedJobs = ref<string[]>(['后端开发'])
const bio = ref('')
const tags = ref<string[]>([])
const tagInput = ref('')
const province = ref('')

const isVolunteer = computed(() => identity.value === '志愿者')
const stepTwoCount = computed(() => isVolunteer.value ? selectedJobs.value.length : selectedDiseases.value.length)

const stepTitle = computed(() => {
  if (currentStep.value === 1) return '选择你的身份'
  if (currentStep.value === 2) return isVolunteer.value ? '选择你的工作岗位' : '选择关注病种'
  return '补充信息'
})

const stepDesc = computed(() => {
  if (currentStep.value === 1) return '这将帮助我们将你提供更准确的服务。'
  if (currentStep.value === 2) {
    return isVolunteer.value
      ? '可多选。我们会根据你的背景推荐更合适的任务、队伍与权限模板。'
      : '可多选。我们会根据你关注的病种提供更准确的需求模板、任务进度和支持内容。'
  }
  return '这些信息能帮助社区更快理解你的经验和协作方向。'
})

const diseases = [
  { name: '罕见神经肌肉病', copy: '如肌营养不良、脊髓性肌萎缩等方向。' },
  { name: '遗传代谢病', copy: '关注筛查、随访、用药与营养管理。' },
  { name: '血液系统罕见病', copy: '围绕症状记录、检查追踪与就医信息。' },
  { name: '罕见肿瘤', copy: '支持病程管理、资料整理与知识查询。' },
  { name: '免疫相关罕见病', copy: '关注长期管理、指标变化与照护协作。' },
  { name: '其他病种', copy: '暂未列出的病种或仍在确认中的情况。' },
]

const jobGroups = [
  { title: '技术研发', items: ['算法工程师', '后端开发', '前端开发', 'UI/UX设计师', '硬件工程师', '其他技术岗位'] },
  { title: '产品与设计', items: ['产品经理', 'UI/UX设计师', '其他产品岗位'] },
  { title: '医疗与科研', items: ['医生/护士', '科研工作者', '其他医疗岗位'] },
  { title: '教育支持', items: ['学生', '志愿者', '其他'] },
]

const provinces = ['北京','上海','天津','重庆','河北','山西','辽宁','吉林','黑龙江','江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南','广东','海南','四川','贵州','云南','陕西','甘肃','青海','内蒙古','广西','西藏','宁夏','新疆','香港','澳门','台湾']

function toggleDisease(d: string) {
  const i = selectedDiseases.value.indexOf(d)
  if (i >= 0) selectedDiseases.value.splice(i, 1)
  else selectedDiseases.value.push(d)
}

function toggleJob(j: string) {
  const i = selectedJobs.value.indexOf(j)
  if (i >= 0) selectedJobs.value.splice(i, 1)
  else selectedJobs.value.push(j)
}

function addTag() {
  const v = tagInput.value.trim()
  if (!v) return
  if (tags.value.length >= 6) { show({ title: '最多添加 6 个标签', variant: 'error' }); return }
  if (!tags.value.includes(v)) tags.value.push(v)
  tagInput.value = ''
}

function removeTag(t: string) { tags.value = tags.value.filter(x => x !== t) }

function goNext() {
  if (currentStep.value === 1 && !identity.value) { show({ title: '请选择一个身份', variant: 'error' }); return }
  if (currentStep.value === 2 && stepTwoCount.value === 0) {
    show({ title: isVolunteer.value ? '请至少选择一个工作岗位' : '请至少选择一个关注病种', variant: 'error' }); return
  }
  if (currentStep.value < 3) { currentStep.value++; return }
  handleSubmit()
}

function goPrev() { if (currentStep.value > 1) currentStep.value-- }

async function handleSubmit() {
  loading.value = true
  try {
    const role = identity.value === '志愿者' ? 'builder' : 'requester'
    const occupation = isVolunteer.value ? selectedJobs.value.join(',') : undefined
    const allTags = [...tags.value]
    if (!isVolunteer.value && selectedDiseases.value.length) {
      allTags.push(...selectedDiseases.value)
    }
    await auth.completeOnboarding({
      role,
      province: province.value || undefined,
      occupation,
      bio: bio.value || undefined,
      tags: allTags.length > 0 ? allTags : undefined,
    })
    show({ title: '初始化已完成，即将进入工作台。', variant: 'success' })
    setTimeout(() => router.push('/hall'), 620)
  } catch {
    show({ title: '提交失败', variant: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page-shell">
    <section class="onboarding-card">
      <div class="human-ornaments" aria-hidden="true">
        <div class="ambient-ring"></div>
        <div class="ambient-nodes"></div>
      </div>

      <header class="card-topbar">
        <div>
          <p class="step-kicker">步骤 {{ currentStep }}/3</p>
          <div class="brand-row">
            <div class="brand-mark">RD</div>
            <div>
              <div class="brand-name">OpenRD</div>
              <span class="brand-caption">Account initialization</span>
            </div>
          </div>
        </div>
        <div class="progress-pill">{{ currentStep }}/3</div>
      </header>

      <div class="content-shell">
        <div class="step-header">
          <h1>{{ stepTitle }}</h1>
          <p class="step-desc">{{ stepDesc }}</p>
        </div>

        <!-- Step 1 -->
        <section v-show="currentStep === 1" class="step-panel">
          <div class="identity-grid">
            <label class="choice-card" :class="{ 'is-selected': identity === '患者' }">
              <input v-model="identity" type="radio" name="identity" value="患者" />
              <span class="radio-dot"></span>
              <span class="choice-title">患者</span>
              <span class="choice-copy">我希望提交个人需求，获得更清晰的工具支持与进度反馈。</span>
            </label>
            <label class="choice-card" :class="{ 'is-selected': identity === '患者家属' }">
              <input v-model="identity" type="radio" name="identity" value="患者家属" />
              <span class="radio-dot"></span>
              <span class="choice-title">患者家属</span>
              <span class="choice-copy">我正在协助家人管理需求，希望代表家属参与平台协作。</span>
            </label>
            <label class="choice-card" :class="{ 'is-selected': identity === '志愿者' }">
              <input v-model="identity" type="radio" name="identity" value="志愿者" />
              <span class="radio-dot"></span>
              <span class="choice-title">志愿者</span>
              <span class="choice-copy">我希望贡献专业能力，参与需求整理、开发、设计或协作支持。</span>
            </label>
          </div>
        </section>

        <!-- Step 2 -->
        <section v-show="currentStep === 2" class="step-panel">
          <div v-if="!isVolunteer" class="disease-grid">
            <label v-for="d in diseases" :key="d.name" class="disease-card" :class="{ 'is-selected': selectedDiseases.includes(d.name) }">
              <input type="checkbox" :checked="selectedDiseases.includes(d.name)" @change="toggleDisease(d.name)" />
              <span><span class="disease-name">{{ d.name }}</span><span class="disease-copy">{{ d.copy }}</span></span>
            </label>
          </div>
          <div v-else class="job-groups">
            <section v-for="g in jobGroups" :key="g.title" class="job-group">
              <h2>{{ g.title }}</h2>
              <div class="checkbox-list">
                <label v-for="j in g.items" :key="j" class="job-chip" :class="{ 'is-selected': selectedJobs.includes(j) }">
                  <input type="checkbox" :checked="selectedJobs.includes(j)" @change="toggleJob(j)" />{{ j }}
                </label>
              </div>
            </section>
          </div>
        </section>

        <!-- Step 3 -->
        <section v-show="currentStep === 3" class="step-panel">
          <div class="optional-grid">
            <div>
              <div class="form-field bio-field">
                <label for="bio">请介绍下你自己 <span class="field-hint">{{ bio.length }}/200</span></label>
                <textarea id="bio" v-model="bio" maxlength="200" placeholder="可以简单介绍你的背景、希望参与的方向，或当前最需要的支持。"></textarea>
              </div>
            </div>
            <div>
              <div class="form-field">
                <label>你擅长的领域 <span class="field-hint">可自定义添加</span></label>
                <div class="tag-panel">
                  <div class="tag-list">
                    <span v-for="t in tags" :key="t" class="tag-chip">{{ t }}<button type="button" @click="removeTag(t)">×</button></span>
                  </div>
                  <div class="tag-input-row">
                    <input v-model="tagInput" class="tag-input" type="text" placeholder="输入标签，如 临床研究" @keydown.enter.prevent="addTag" />
                    <button class="add-tag-button" type="button" @click="addTag">添加</button>
                  </div>
                </div>
              </div>
              <div class="form-field">
                <label for="province">所在地区</label>
                <select id="province" v-model="province">
                  <option value="">请选择省份</option>
                  <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
                </select>
              </div>
            </div>
          </div>
        </section>
      </div>

      <footer class="card-footer">
        <div class="footer-meta">
          <span>当前步骤 {{ currentStep }}/3</span>
          <span v-if="currentStep === 2" class="selection-count">已选择 {{ stepTwoCount }} 项</span>
        </div>
        <div class="footer-actions">
          <OrdButton v-show="currentStep > 1" variant="ghost" class="footer-btn" type="button" @click="goPrev">上一步</OrdButton>
          <OrdButton variant="primary" :loading="loading" class="footer-btn" type="button" @click="goNext">
            {{ currentStep === 3 ? (loading ? '正在完成' : '完成') : '下一步' }}
          </OrdButton>
        </div>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.page-shell {
  min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 32px;
  background:
    radial-gradient(circle at 24% 22%, rgba(255, 174, 19, 0.06), transparent 24%),
    radial-gradient(circle at 76% 18%, rgba(237, 82, 203, 0.045), transparent 22%),
    radial-gradient(circle at 12% 10%, rgba(20, 110, 245, 0.07), transparent 28%),
    radial-gradient(circle at 88% 82%, rgba(122, 61, 255, 0.065), transparent 30%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.onboarding-card {
  position: relative; width: min(1460px, 100%); min-height: 640px;
  display: flex; flex-direction: column; overflow: hidden;
  background: var(--ord-color-white); border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: 8px; box-shadow: var(--ord-shadow-cascade);
}

.onboarding-card::before {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(rgba(20, 110, 245, 0.018) 1px, transparent 1px), linear-gradient(90deg, rgba(20, 110, 245, 0.018) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(115deg, transparent 0%, #000 18%, #000 72%, transparent 100%);
  pointer-events: none;
}

.onboarding-card::after {
  content: ""; position: absolute; width: 420px; height: 420px; right: -180px; top: -220px;
  border: 1px solid rgba(255, 174, 19, 0.12); border-radius: 50%; pointer-events: none;
}

.human-ornaments { position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 1; }
.ambient-ring { position: absolute; right: 42px; top: 112px; width: 180px; height: 180px; border: 1px solid rgba(255, 174, 19, 0.16); border-radius: 50%; }
.ambient-ring::before { content: ""; position: absolute; inset: 36px; border: 1px solid rgba(237, 82, 203, 0.08); border-radius: 50%; }
.ambient-ring::after { content: ""; position: absolute; width: 8px; height: 8px; right: 28px; top: 26px; background: rgba(255, 174, 19, 0.38); border-radius: 50%; }
.ambient-nodes { position: absolute; left: 40px; bottom: 78px; width: 160px; height: 72px; background: radial-gradient(circle at 8px 14px, rgba(20, 110, 245, 0.3) 0 4px, transparent 5px), radial-gradient(circle at 78px 34px, rgba(0, 215, 34, 0.24) 0 5px, transparent 6px), radial-gradient(circle at 142px 16px, rgba(237, 82, 203, 0.24) 0 4px, transparent 5px); }

.card-topbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 22px 32px 16px; border-bottom: 1px solid #ececec; position: relative; z-index: 2; }
.step-kicker { margin: 0 0 8px; color: var(--ord-color-blue); font-size: 13px; font-weight: 600; line-height: 1.3; letter-spacing: 1.5px; text-transform: uppercase; }
.brand-row { display: inline-flex; align-items: center; gap: 12px; color: var(--ord-color-black); }
.brand-mark { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 4px; background: var(--ord-color-blue); color: var(--ord-color-white); font-size: 15px; font-weight: 600; letter-spacing: -0.3px; }
.brand-name { font-size: 20px; font-weight: 600; line-height: 1.2; letter-spacing: -0.2px; }
.brand-caption { display: block; margin-top: 2px; color: var(--ord-color-gray-300); font-size: 12px; font-weight: 550; letter-spacing: 1.1px; text-transform: uppercase; }
.progress-pill { min-width: 82px; padding: 8px 12px; color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); border: 1px solid rgba(20, 110, 245, 0.18); border-radius: 4px; font-size: 14px; font-weight: 600; text-align: center; }

.content-shell { flex: 1; display: grid; grid-template-rows: auto 1fr; min-height: 0; padding: 24px 32px; position: relative; z-index: 2; }
.step-header { max-width: 820px; margin-bottom: 18px; }
h1 { margin: 0; color: var(--ord-color-black); font-size: clamp(36px, 4vw, 48px); font-weight: 600; line-height: 1.04; letter-spacing: -0.8px; }
.step-desc { margin: 12px 0 0; color: var(--ord-color-gray-500); font-size: 16px; font-weight: 500; line-height: 1.5; }

.step-panel { min-height: 0; }

.identity-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.choice-card { position: relative; display: block; min-height: 170px; padding: 18px; cursor: pointer; background: #fff; border: 1px solid var(--ord-color-border); border-radius: 8px; transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease; }
.choice-card:hover { border-color: var(--ord-color-blue); box-shadow: 0 14px 28px rgba(20, 110, 245, 0.12); transform: translateX(6px); }
.choice-card input { position: absolute; opacity: 0; pointer-events: none; }
.radio-dot { width: 20px; height: 20px; display: inline-grid; place-items: center; margin-bottom: 26px; border: 1px solid var(--ord-color-border-hover); border-radius: 50%; background: #fff; }
.radio-dot::after { content: ""; width: 10px; height: 10px; border-radius: 50%; background: var(--ord-color-blue); opacity: 0; }
.choice-card.is-selected .radio-dot { border-color: var(--ord-color-blue); }
.choice-card.is-selected .radio-dot::after { opacity: 1; }
.choice-card.is-selected { border-color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.05); box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.08); }
.choice-title { display: block; margin-bottom: 10px; color: var(--ord-color-black); font-size: 24px; font-weight: 600; line-height: 1.3; }
.choice-copy { display: block; color: var(--ord-color-gray-500); font-size: 15px; line-height: 1.55; }

.disease-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.disease-card { display: flex; align-items: flex-start; gap: 12px; min-height: 106px; padding: 16px; cursor: pointer; background: #fff; border: 1px solid var(--ord-color-border); border-radius: 8px; transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease; }
.disease-card:hover { border-color: var(--ord-color-blue); box-shadow: 0 14px 28px rgba(20, 110, 245, 0.1); transform: translateX(6px); }
.disease-card input { width: 16px; height: 16px; margin-top: 2px; accent-color: var(--ord-color-blue); flex: 0 0 auto; }
.disease-card.is-selected { border-color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.05); box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.08); }
.disease-name { display: block; color: var(--ord-color-black); font-size: 17px; font-weight: 600; line-height: 1.3; }
.disease-copy { display: block; margin-top: 6px; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }

.job-groups { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.job-group { padding: 14px; background: #fff; border: 1px solid var(--ord-color-border); border-radius: 8px; }
.job-group h2 { margin: 0 0 12px; color: var(--ord-color-black); font-size: 16px; font-weight: 600; line-height: 1.3; }
.checkbox-list { display: flex; flex-wrap: wrap; gap: 8px; }
.job-chip { display: inline-flex; align-items: center; gap: 10px; min-height: 34px; padding: 0 10px; color: var(--ord-color-gray-700); background: #fff; border: 1px solid var(--ord-color-border); border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; line-height: 1.4; transition: border-color 180ms ease, color 180ms ease, background 180ms ease; }
.job-chip:hover { border-color: var(--ord-color-blue); color: var(--ord-color-blue); }
.job-chip input { width: 16px; height: 16px; accent-color: var(--ord-color-blue); }
.job-chip.is-selected { color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); border-color: rgba(20, 110, 245, 0.24); }

.optional-grid { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 22px; height: 100%; min-height: 0; align-items: stretch; }
.optional-grid > div { min-height: 0; display: flex; flex-direction: column; }
.form-field { margin-bottom: 18px; }
.bio-field { flex: 1; display: flex; flex-direction: column; margin-bottom: 0; min-height: 0; }
.form-field label { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; color: var(--ord-color-gray-800); font-size: 14px; font-weight: 600; line-height: 1.4; }
.field-hint { color: var(--ord-color-gray-300); font-size: 12px; font-weight: 500; }
textarea, select, .text-input { width: 100%; color: var(--ord-color-black); background: var(--ord-color-white); border: 1px solid var(--ord-color-border); border-radius: 4px; outline: none; font-size: 15px; font-weight: 500; line-height: 1.55; transition: border-color 180ms ease, box-shadow 180ms ease; }
.text-input { height: 46px; padding: 0 12px; }
textarea { flex: 1; min-height: 160px; resize: none; padding: 12px; }
select { height: 46px; padding: 0 12px; cursor: pointer; }
textarea:hover, select:hover, .text-input:hover { border-color: var(--ord-color-border-hover); }
textarea:focus, select:focus, .text-input:focus { border-color: var(--ord-color-blue); box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.12); }

.tag-panel { padding: 16px; border: 1px solid var(--ord-color-border); border-radius: 8px; flex: 1; display: flex; flex-direction: column; min-height: 0; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; flex: 1; align-content: flex-start; margin-bottom: 12px; }
.tag-chip { display: inline-flex; align-items: center; gap: 8px; min-height: 32px; padding: 0 10px; color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); border: 1px solid rgba(20, 110, 245, 0.18); border-radius: 4px; font-size: 13px; font-weight: 600; }
.tag-chip button { padding: 0; color: var(--ord-color-blue); background: transparent; border: 0; cursor: pointer; font-size: 16px; line-height: 1; }
.tag-input-row { display: grid; grid-template-columns: 1fr auto; gap: 10px; }
.tag-input { height: 42px; padding: 0 12px; width: 100%; color: var(--ord-color-black); background: var(--ord-color-white); border: 1px solid var(--ord-color-border); border-radius: 4px; outline: none; font-size: 15px; font-weight: 500; transition: border-color 180ms ease, box-shadow 180ms ease; }
.tag-input:hover { border-color: var(--ord-color-border-hover); }
.tag-input:focus { border-color: var(--ord-color-blue); box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.12); }
.add-tag-button { height: 44px; padding: 0 16px; color: var(--ord-color-gray-700); background: #fff; border: 1px solid var(--ord-color-border); border-radius: 4px; cursor: pointer; font-size: 15px; font-weight: 600; white-space: nowrap; transition: transform 180ms ease, color 180ms ease, border-color 180ms ease; }
.add-tag-button:hover { border-color: var(--ord-color-blue); color: var(--ord-color-blue); transform: translateX(6px); }

.card-footer { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 16px 32px 22px; border-top: 1px solid #ececec; position: relative; z-index: 2; }
.footer-meta { display: flex; align-items: center; gap: 14px; color: var(--ord-color-gray-500); font-size: 14px; line-height: 1.4; }
.selection-count { padding: 7px 10px; color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); border-radius: 4px; font-weight: 600; }
.footer-actions { display: flex; align-items: center; gap: 12px; }

.footer-btn :deep(.ord-button) {
  min-width: 132px;
  height: 44px;
  padding: 0 22px;
  font-size: 15px;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 991px) {
  .page-shell { padding: 24px; }
  .onboarding-card { height: auto; min-height: 640px; }
  .identity-grid, .disease-grid, .job-groups, .optional-grid { grid-template-columns: 1fr; }
  .ambient-ring { display: none; }
  .ambient-nodes { opacity: 0.5; }
}

@media (max-width: 767px) {
  .page-shell { padding: 0; align-items: stretch; background: var(--ord-color-white); }
  .onboarding-card { width: 100%; min-height: 100vh; border: 0; border-radius: 0; box-shadow: none; }
  .card-topbar, .content-shell, .card-footer { padding-left: 22px; padding-right: 22px; }
  .card-topbar { align-items: flex-start; flex-direction: column; }
  h1 { font-size: 36px; }
  .choice-card { min-height: 150px; }
  .card-footer { align-items: stretch; flex-direction: column; }
  .footer-meta { justify-content: space-between; }
  .footer-actions { display: grid; grid-template-columns: 1fr 1fr; }
  .primary-button, .secondary-button { width: 100%; }
  .human-ornaments { display: none; }
}

@media (max-width: 479px) {
  .content-shell { padding-top: 24px; }
  .card-topbar, .content-shell, .card-footer { padding-left: 18px; padding-right: 18px; }
  .brand-mark { width: 34px; height: 34px; }
  .brand-name { font-size: 18px; }
  .brand-caption { font-size: 10px; }
  h1 { font-size: 32px; }
  .tag-input-row, .footer-actions { grid-template-columns: 1fr; }
  .choice-card:hover, .add-tag-button:hover, .secondary-button:hover, .primary-button:hover { transform: translateX(0); }
}
</style>
