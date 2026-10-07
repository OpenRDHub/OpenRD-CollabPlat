import { onBeforeUnmount, onMounted } from 'vue'

const EDITABLE_SELECTOR = 'input:not([type="hidden"]), textarea, select, [contenteditable="true"]'

export function useMobileInputVisibility() {
  let activeElement: HTMLElement | null = null
  let scrollTimer: number | undefined

  function keepVisible(element: HTMLElement) {
    if (!window.matchMedia('(max-width: 767px)').matches) return

    window.clearTimeout(scrollTimer)
    scrollTimer = window.setTimeout(() => {
      if (document.activeElement !== element) return
      element.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }, 180)
  }

  function handleFocusIn(event: FocusEvent) {
    const target = event.target
    if (!(target instanceof HTMLElement) || !target.matches(EDITABLE_SELECTOR)) return
    activeElement = target
    keepVisible(target)
  }

  function handleFocusOut(event: FocusEvent) {
    if (event.target === activeElement) activeElement = null
  }

  function handleViewportResize() {
    if (activeElement) keepVisible(activeElement)
  }

  onMounted(() => {
    document.addEventListener('focusin', handleFocusIn)
    document.addEventListener('focusout', handleFocusOut)
    window.visualViewport?.addEventListener('resize', handleViewportResize)
  })

  onBeforeUnmount(() => {
    window.clearTimeout(scrollTimer)
    document.removeEventListener('focusin', handleFocusIn)
    document.removeEventListener('focusout', handleFocusOut)
    window.visualViewport?.removeEventListener('resize', handleViewportResize)
  })
}
