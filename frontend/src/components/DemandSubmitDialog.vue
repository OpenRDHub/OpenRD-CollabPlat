<script setup lang="ts">
import { ref, computed } from 'vue'
import { OrdDialog, OrdInput, OrdTextarea, OrdButton, OrdFileUpload, useToast } from '@/components/ui'
import { demandsApi } from '@/api'
import type { DemandSubmitPayload } from '@/api/demands'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'submit-success': []
}>()

const { show: showToast } = useToast()

const formData = ref<DemandSubmitPayload>({
  title: '',
  description: '',
  contact_phone: '',
  wechat_id: '',
  attachment_ids: [],
})

const uploadedFiles = ref<Array<{ id: string; name: string }>>([])
const privacyConfirmed = ref(false)
const isSubmitting = ref(false)
const formMessage = ref('')

const isFormValid = computed(() => {
  return (
    formData.value.title.trim().length > 0 &&
    formData.value.description.trim().length > 0 &&
    (formData.value.contact_phone.trim().length > 0 || formData.value.wechat_id.trim().length > 0) &&
    privacyConfirmed.value
  )
})

const handleFileChange = async (files: File[]) => {
  if (files.length === 0) return

  const file = files[0]
  if (!file) return

  try {
    // 模拟文件上传，实际应该调用 filesApi.upload
    // const response = await filesApi.upload(file)

    // Mock 实现
    const mockFileId = `file_${Date.now()}`
    uploadedFiles.value.push({
      id: mockFileId,
      name: file.name,
    })
    formData.value.attachment_ids = uploadedFiles.value.map(f => f.id)

    showToast({
      title: '附件上传成功',
      description: file.name,
      variant: 'success',
    })
  } catch (error) {
    showToast({
      title: '附件上传失败',
      description: '请重试或联系管理员',
      variant: 'error',
    })
  }
}

const handleRemoveFile = (fileId: string) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== fileId)
  formData.value.attachment_ids = uploadedFiles.value.map(f => f.id)
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    formMessage.value = '请完整填写必填项并确认隐私条款'
    return
  }

  isSubmitting.value = true
  formMessage.value = ''

  try {
    await demandsApi.submit(formData.value)

    showToast({
      title: '需求已提交',
      description: '产品经理会尽快审核。',
      variant: 'success',
    })

    // 重置表单
    formData.value = {
      title: '',
      description: '',
      contact_phone: '',
      wechat_id: '',
      attachment_ids: [],
    }
    uploadedFiles.value = []
    privacyConfirmed.value = false

    emit('submit-success')
    emit('update:open', false)
  } catch (error: any) {
    formMessage.value = error.message || '提交失败，请稍后重试'
    showToast({
      title: '提交失败',
      description: formMessage.value,
      variant: 'error',
    })
  } finally {
    isSubmitting.value = false
  }
}

const handleClose = () => {
  emit('update:open', false)
}
</script>

<template>
  <OrdDialog :open="open" @update:open="(val: boolean) => emit('update:open', val)">
    <div class="demand-submit-dialog">
      <header class="modal-header">
        <div>
          <p class="section-label">Submit Demand</p>
          <h2>提交新的需求</h2>
          <p class="modal-description">
            请尽量描述你遇到的问题、期待的结果和可联系到你的方式。产品经理审核后会协助转化为任务。
          </p>
        </div>
        <button class="close-button" type="button" aria-label="关闭弹窗" @click="handleClose">
          ×
        </button>
      </header>

      <form class="demand-form" @submit.prevent="handleSubmit">
        <div class="form-grid">
          <div class="form-field is-full">
            <label for="demandTitle">需求标题</label>
            <OrdInput
              id="demandTitle"
              v-model="formData.title"
              type="text"
              placeholder="例如：希望记录复诊前的问题清单"
              required
            />
          </div>

          <div class="form-field is-full">
            <label for="demandDetail">需求详情</label>
            <OrdTextarea
              id="demandDetail"
              v-model="formData.description"
              placeholder="请描述遇到的问题、使用场景、希望平台或志愿者提供什么帮助。"
              :rows="6"
              required
            />
          </div>

          <div class="form-field">
            <label for="contactPhone">联系电话</label>
            <OrdInput
              id="contactPhone"
              v-model="formData.contact_phone"
              type="tel"
              placeholder="可选，便于产品经理沟通"
            />
          </div>

          <div class="form-field">
            <label for="wechatId">微信号</label>
            <OrdInput
              id="wechatId"
              v-model="formData.wechat_id"
              type="text"
              placeholder="可选，电话/微信至少填一项"
            />
          </div>

          <div class="form-field is-full">
            <label for="attachmentInput">附件</label>
            <OrdFileUpload
              id="attachmentInput"
              accept="image/jpeg,image/png,image/jpg,.pdf,.doc,.docx"
              @change="handleFileChange"
            >
              <div class="upload-zone">
                <span class="upload-title">点击或拖拽附件到这里</span>
                <span class="upload-hint">
                  可上传病历截图、需求草图、说明文档等；支持 JPG/PNG/PDF/DOC，单个文件最大 10MB。
                </span>
              </div>
            </OrdFileUpload>

            <div v-if="uploadedFiles.length > 0" class="file-list">
              <div
                v-for="file in uploadedFiles"
                :key="file.id"
                class="file-item"
              >
                <span class="file-name">{{ file.name }}</span>
                <button
                  type="button"
                  class="remove-file"
                  @click="handleRemoveFile(file.id)"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <label class="privacy-check">
          <input
            id="privacyConfirm"
            v-model="privacyConfirmed"
            type="checkbox"
          />
          <span>
            我已确认不上传非必要敏感信息，并同意平台为需求审核和沟通目的保护性使用联系方式。
          </span>
        </label>

        <div class="modal-footer">
          <span v-if="formMessage" class="form-message" role="status" aria-live="polite">
            {{ formMessage }}
          </span>
          <OrdButton
            type="submit"
            variant="primary"
            :disabled="!isFormValid || isSubmitting"
            :loading="isSubmitting"
          >
            提交需求
          </OrdButton>
        </div>
      </form>
    </div>
  </OrdDialog>
</template>

<style scoped>
.demand-submit-dialog {
  width: min(720px, calc(100vw - 48px));
  max-height: min(760px, calc(100vh - 48px));
  overflow-y: auto;
  background: var(--ord-color-white);
  border: 1px solid rgba(216, 216, 216, 0.92);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 24px 24px 18px;
  border-bottom: 1px solid #ececec;
}

.section-label {
  margin: 0 0 8px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  line-height: 1.3;
  text-transform: uppercase;
}

.modal-header h2 {
  margin: 0 0 10px;
  color: var(--ord-color-black);
  font-size: 34px;
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.6px;
}

.modal-description {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  line-height: 1.55;
}

.close-button {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--ord-color-gray-500);
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 22px;
  font-weight: 400;
  line-height: 1;
  transition: var(--ord-transition-base);
}

.close-button:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
  transform: translateX(4px);
}

.demand-form {
  padding: 22px 24px 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.form-field {
  display: grid;
  gap: 8px;
}

.form-field.is-full {
  grid-column: 1 / -1;
}

.form-field label {
  color: var(--ord-color-gray-800);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.upload-zone {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 116px;
  padding: 18px;
  text-align: center;
  background: rgba(20, 110, 245, 0.045);
  border: 1px dashed rgba(20, 110, 245, 0.38);
  border-radius: var(--ord-radius-md);
  cursor: pointer;
  transition: var(--ord-transition-base);
}

.upload-zone:hover {
  background: rgba(20, 110, 245, 0.1);
  border-color: var(--ord-color-blue);
}

.upload-title {
  display: block;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 600;
}

.upload-hint {
  display: block;
  margin-top: 6px;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(20, 110, 245, 0.06);
  border: 1px solid rgba(20, 110, 245, 0.12);
  border-radius: var(--ord-radius-sm);
}

.file-name {
  flex: 1;
  color: var(--ord-color-black);
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  flex-shrink: 0;
  padding: 4px 10px;
  color: var(--ord-color-red);
  background: transparent;
  border: 1px solid var(--ord-color-red);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: var(--ord-transition-base);
}

.remove-file:hover {
  color: var(--ord-color-white);
  background: var(--ord-color-red);
}

.privacy-check {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  color: var(--ord-color-gray-700);
  font-weight: 500;
}

.privacy-check input[type='checkbox'] {
  width: 16px;
  height: 16px;
  margin-top: 2px;
  flex: 0 0 auto;
  accent-color: var(--ord-color-blue);
  cursor: pointer;
}

.privacy-check span {
  color: var(--ord-color-gray-700);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 20px;
}

.form-message {
  min-height: 20px;
  color: var(--ord-color-red);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

@media (max-width: 520px) {
  .demand-submit-dialog {
    width: calc(100vw - 28px);
  }

  .modal-header {
    padding-left: 18px;
    padding-right: 18px;
  }

  .modal-header h2 {
    font-size: 30px;
  }

  .demand-form {
    padding-left: 18px;
    padding-right: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
