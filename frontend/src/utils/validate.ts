/** 中国大陆手机号：1 开头，第二位 3-9，共 11 位数字 */
const PHONE_RE = /^1[3-9]\d{9}$/

/** 校验手机号，返回错误文案；合法时返回空字符串 */
export function validatePhone(value: string): string {
  const phone = value.trim()
  if (!phone) return '请输入手机号'
  if (!/^\d+$/.test(phone)) return '手机号只能为数字'
  if (phone.length !== 11) return '手机号应为 11 位数字'
  if (!PHONE_RE.test(phone)) return '手机号格式不正确'
  return ''
}

/** 只判断是否合法 */
export function isPhone(value: string): boolean {
  return PHONE_RE.test(value.trim())
}