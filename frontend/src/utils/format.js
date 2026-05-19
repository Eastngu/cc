export function formatCurrency(value) {
  if (value == null) return '¥0.00'
  return `¥${Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

export function formatDate(dateStr) {
  if (!dateStr) return '-'
  return dateStr.slice(0, 10)
}

export const billingTypeMap = {
  area: '按面积(dm²)',
  weight: '按重量(kg)',
  piece: '按件数',
}
