import { http, HttpResponse } from 'msw'
import type { AdminDemand, DemandStats } from '@/api/admin-demands'
import { demands } from '../data/demands'
import { users } from '../data/users'

// 只持久化运营侧的变更字段（review_status / convert_status / task_id / progress / feedback / title）
const PATCHES_KEY = 'openrd_mock_admin_demand_patches'

type DemandPatch = Partial<Pick<AdminDemand, 'title' | 'review_status' | 'convert_status' | 'task_id' | 'progress' | 'feedback' | 'updated_at'>>

function loadPatches(): Record<string, DemandPatch> {
  try {
    const raw = localStorage.getItem(PATCHES_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return {}
}

function savePatches(patches: Record<string, DemandPatch>) {
  try {
    localStorage.setItem(PATCHES_KEY, JSON.stringify(patches))
  } catch {}
}

const patches = loadPatches()

// 将 MockDemand 映射为 AdminDemand，叠加运营侧的持久化变更
function toAdminDemand(d: typeof demands[number]): AdminDemand {
  const creator = users.find((u) => u.id === d.creator_id)
  const patch = patches[d.id] ?? {}
  return {
    id: d.id,
    title: patch.title ?? d.title,
    description: d.description,
    submitted_at: d.created_at.slice(0, 10),
    review_status: (patch.review_status ?? d.status) as AdminDemand['review_status'],
    convert_status: (patch.convert_status ?? d.convert_status) as AdminDemand['convert_status'],
    publisher: creator?.nickname ?? '未知用户',
    publisher_id: d.creator_id,
    task_id: patch.task_id !== undefined ? patch.task_id : (d.linked_task_id || null),
    progress: patch.progress ?? d.progress,
    feedback: patch.feedback ?? d.feedback,
    urgency: d.urgency,
    contact_phone: d.contact_phone,
    created_at: d.created_at,
    updated_at: patch.updated_at ?? d.updated_at,
  }
}

export const adminDemandsHandlers = [
  // 获取需求列表
  http.get('/api/v1/admin/demands', ({ request }) => {
    const url = new URL(request.url)
    const keyword = url.searchParams.get('keyword') || ''
    const reviewStatus = url.searchParams.get('review_status')
    const convertStatus = url.searchParams.get('convert_status')

    let filtered = demands
      .filter((d) => d.is_deleted === 0)
      .map(toAdminDemand)

    if (keyword) {
      const q = keyword.toLowerCase()
      filtered = filtered.filter(
        (d) =>
          d.id.toLowerCase().includes(q) ||
          d.title.toLowerCase().includes(q) ||
          d.publisher.toLowerCase().includes(q) ||
          d.task_id?.toLowerCase().includes(q),
      )
    }

    if (reviewStatus && reviewStatus !== '全部') {
      filtered = filtered.filter((d) => d.review_status === reviewStatus)
    }

    if (convertStatus && convertStatus !== '全部') {
      filtered = filtered.filter((d) => d.convert_status === convertStatus)
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: { items: filtered, total: filtered.length, page: 1, page_size: 1000 },
    })
  }),

  // 获取统计数据
  http.get('/api/v1/admin/demands/stats', () => {
    const all = demands.filter((d) => d.is_deleted === 0).map(toAdminDemand)
    const stats: DemandStats = {
      total: all.length,
      pending: all.filter((d) => d.review_status === '待审核').length,
      talking: all.filter((d) => d.review_status === '沟通中').length,
      converted: all.filter((d) => d.review_status === '已转任务').length,
      closed: all.filter((d) => d.review_status === '已关闭').length,
    }
    return HttpResponse.json({ code: 0, message: 'success', data: stats })
  }),

  // 获取单个需求详情
  http.get('/api/v1/admin/demands/:id', ({ params }) => {
    const source = demands.find((d) => d.id === params.id && d.is_deleted === 0)
    if (!source) {
      return HttpResponse.json({ code: 404, message: 'Demand not found', data: null }, { status: 404 })
    }
    return HttpResponse.json({ code: 0, message: 'success', data: toAdminDemand(source) })
  }),

  // 更新需求（运营侧变更写入 patches）
  http.patch('/api/v1/admin/demands/:id', async ({ params, request }) => {
    const source = demands.find((d) => d.id === params.id && d.is_deleted === 0)
    if (!source) {
      return HttpResponse.json({ code: 404, message: 'Demand not found', data: null }, { status: 404 })
    }

    const body = (await request.json()) as DemandPatch
    patches[params.id as string] = {
      ...patches[params.id as string],
      ...body,
      updated_at: new Date().toISOString(),
    }
    savePatches(patches)

    return HttpResponse.json({ code: 0, message: 'success', data: toAdminDemand(source) })
  }),

  // 导出需求
  http.get('/api/v1/admin/demands/export', () => {
    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: { url: '/downloads/demands-export.csv', filename: 'demands-export.csv' },
    })
  }),
]
