<script setup lang="ts">
import { OrdToastProvider } from '@/components/ui'
import { useToast } from '@/components/ui/toast/useToast'
import OrdToast from '@/components/ui/toast/OrdToast.vue'

const { toasts, dismiss } = useToast()
</script>

<template>
  <OrdToastProvider>
    <RouterView />
    <OrdToast
      v-for="toast in toasts"
      :key="toast.id"
      :title="toast.title"
      :description="toast.description"
      :variant="toast.variant"
      @close="dismiss(toast.id)"
    />
  </OrdToastProvider>
</template>

<style scoped></style>
