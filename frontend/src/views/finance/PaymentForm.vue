<template>
  <el-dialog
    :title="type === 'receive' ? '登记收款' : '登记付款'"
    :model-value="visible"
    width="520px"
    @open="handleOpen"
    @close="$emit('update:visible', false)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <!-- receive: customer + receivable -->
      <template v-if="type === 'receive'">
        <el-form-item label="客户" prop="customer">
          <el-select
            v-model="form.customer"
            placeholder="请选择客户"
            filterable
            style="width: 100%"
            @change="handleCustomerChange"
          >
            <el-option
              v-for="c in customerOptions"
              :key="c.id"
              :value="c.id"
              :label="c.short_name || c.name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="应收单" prop="receivable">
          <el-select
            v-model="form.receivable"
            placeholder="请选择应收单（可选）"
            clearable
            style="width: 100%"
            :disabled="!form.customer"
            @change="handleReceivableChange"
          >
            <el-option
              v-for="r in receivableOptions"
              :key="r.id"
              :value="r.id"
              :label="`${r.receivable_no}（余额 ${formatCurrency(r.balance)}）`"
            />
          </el-select>
        </el-form-item>
      </template>

      <!-- pay: payable -->
      <template v-else>
        <el-form-item label="应付单" prop="payable">
          <el-select
            v-model="form.payable"
            placeholder="请选择应付单"
            filterable
            style="width: 100%"
            @change="handlePayableChange"
          >
            <el-option
              v-for="p in payableOptions"
              :key="p.id"
              :value="p.id"
              :label="`${p.payable_no} ${p.supplier_name}（余额 ${formatCurrency(p.balance)}）`"
            />
          </el-select>
        </el-form-item>
      </template>

      <el-form-item label="金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :min="0.01"
          :precision="2"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="支付方式" prop="payment_method">
        <el-select v-model="form.payment_method" style="width: 100%">
          <el-option value="transfer" label="银行转账" />
          <el-option value="cash" label="现金" />
          <el-option value="acceptance" label="承兑汇票" />
        </el-select>
      </el-form-item>

      <el-form-item label="日期" prop="payment_date">
        <el-date-picker
          v-model="form.payment_date"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="备注信息"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getCustomers } from '@/api/customers'
import { getReceivables, getPayables, createPayment } from '@/api/finance'
import { formatCurrency } from '@/utils/format'

const props = defineProps({
  visible: Boolean,
  type: { type: String, default: 'receive' }, // 'receive' | 'pay'
  presetCustomer: { type: Number, default: null },
  presetReceivable: { type: Number, default: null },
  presetPayable: { type: Number, default: null },
})

const emit = defineEmits(['update:visible', 'saved'])

const formRef = ref(null)
const submitting = ref(false)
const customerOptions = ref([])
const receivableOptions = ref([])
const payableOptions = ref([])

function getTodayStr() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const form = reactive({
  customer: null,
  receivable: null,
  payable: null,
  amount: 0,
  payment_method: 'transfer',
  payment_date: getTodayStr(),
  remark: '',
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  payable: [{ required: true, message: '请选择应付单', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    {
      validator: (_, value, cb) => {
        if (!value || value <= 0) cb(new Error('金额必须大于0'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }],
  payment_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

async function loadCustomers() {
  try {
    const { data } = await getCustomers({ page_size: 200 })
    customerOptions.value = data.results
  } catch {
    // Handled by interceptor
  }
}

async function loadReceivables(customerId) {
  if (!customerId) {
    receivableOptions.value = []
    return
  }
  try {
    const { data } = await getReceivables({ customer: customerId, page_size: 200 })
    receivableOptions.value = data.results.filter((r) => r.status !== 'settled')
  } catch {
    // Handled by interceptor
  }
}

async function loadPayables() {
  try {
    const { data } = await getPayables({ page_size: 200 })
    payableOptions.value = data.results.filter((p) => p.status !== 'settled')
  } catch {
    // Handled by interceptor
  }
}

function handleCustomerChange(customerId) {
  form.receivable = null
  loadReceivables(customerId)
}

function handleReceivableChange(receivableId) {
  if (!receivableId) return
  const rec = receivableOptions.value.find((r) => r.id === receivableId)
  if (rec) form.amount = Number(rec.balance)
}

function handlePayableChange(payableId) {
  if (!payableId) return
  const p = payableOptions.value.find((item) => item.id === payableId)
  if (p) form.amount = Number(p.balance)
}

function resetForm() {
  Object.assign(form, {
    customer: null,
    receivable: null,
    payable: null,
    amount: 0,
    payment_method: 'transfer',
    payment_date: getTodayStr(),
    remark: '',
  })
  receivableOptions.value = []
  formRef.value?.clearValidate()
}

async function handleOpen() {
  resetForm()

  if (props.type === 'receive') {
    await loadCustomers()
    if (props.presetCustomer) {
      form.customer = props.presetCustomer
      await loadReceivables(props.presetCustomer)
      if (props.presetReceivable) {
        form.receivable = props.presetReceivable
        handleReceivableChange(props.presetReceivable)
      }
    }
  } else {
    await loadPayables()
    if (props.presetPayable) {
      form.payable = props.presetPayable
      handlePayableChange(props.presetPayable)
    }
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      type: props.type,
      amount: form.amount,
      payment_method: form.payment_method,
      payment_date: form.payment_date,
      remark: form.remark,
    }
    if (props.type === 'receive') {
      payload.customer = form.customer
      if (form.receivable) payload.receivable = form.receivable
    } else {
      payload.payable = form.payable
    }
    await createPayment(payload)
    ElMessage.success(props.type === 'receive' ? '收款登记成功' : '付款登记成功')
    emit('update:visible', false)
    emit('saved')
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}

watch(
  () => props.visible,
  (val) => {
    if (!val) {
      setTimeout(resetForm, 300)
    }
  }
)
</script>
