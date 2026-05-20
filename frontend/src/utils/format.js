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

export const orderStatusMap = {
  pending: { label: '待加工', type: 'info' },
  processing: { label: '加工中', type: 'warning' },
  completed: { label: '已完工', type: 'success' },
  shipped: { label: '已出货', type: '' },
}

export const unitMap = {
  area: 'dm²',
  weight: 'kg',
  piece: '件',
}

export const receivableStatusMap = {
  open: { label: '未结', type: 'danger' },
  partial: { label: '部分回款', type: 'warning' },
  settled: { label: '已结清', type: 'success' },
}

export const payableStatusMap = {
  open: { label: '未付', type: 'danger' },
  partial: { label: '部分付款', type: 'warning' },
  settled: { label: '已结清', type: 'success' },
}

export const paymentMethodMap = {
  transfer: '银行转账',
  cash: '现金',
  acceptance: '承兑汇票',
}

export const payableCategoryMap = {
  material: '原料',
  electricity: '电费',
  equipment: '设备',
  other: '其他',
}

export const statementStatusMap = {
  draft: { label: '草稿', type: 'info' },
  confirmed: { label: '已确认', type: 'success' },
  sent: { label: '已发送', type: '' },
}
