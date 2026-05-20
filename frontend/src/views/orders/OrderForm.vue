<template>
  <el-dialog
    :title="isEdit ? '编辑订单' : '新建订单'"
    :model-value="visible"
    width="640px"
    @open="handleOpen"
    @close="$emit('update:visible', false)"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="客户" prop="customer">
        <el-select
          v-model="form.customer"
          placeholder="请选择客户"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="c in customerOptions"
            :key="c.id"
            :value="c.id"
            :label="c.short_name || c.name"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="镀种工艺" prop="plating_process">
        <el-select
          v-model="form.plating_process"
          placeholder="请选择镀种工艺"
          style="width: 100%"
          @change="handleProcessChange"
        >
          <el-option
            v-for="p in processOptions"
            :key="p.id"
            :value="p.id"
            :label="p.name"
          >
            <span>{{ p.name }}</span>
            <span style="float: right; color: #909399; font-size: 12px">{{ p.code }}</span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="产品名称" prop="product_name">
        <el-input v-model="form.product_name" placeholder="请输入产品名称" />
      </el-form-item>

      <el-form-item label="产品规格">
        <el-input v-model="form.product_spec" placeholder="如: 50×30mm" />
      </el-form-item>

      <el-form-item label="数量" prop="quantity">
        <el-input-number
          v-model="form.quantity"
          :min="0"
          :precision="4"
          style="width: 200px"
        />
        <span style="margin-left: 8px; color: #606266">{{ unitLabel }}</span>
      </el-form-item>

      <el-form-item label="单价" prop="unit_price">
        <el-input-number
          v-model="form.unit_price"
          :min="0"
          :precision="4"
          style="width: 200px"
        />
        <span style="margin-left: 8px; color: #606266">元 / {{ unitLabel }}</span>
      </el-form-item>

      <el-form-item label="预计金额">
        <span class="total-amount">{{ formatCurrency(totalAmount) }}</span>
      </el-form-item>

      <el-form-item label="来料日期" prop="received_at">
        <el-date-picker
          v-model="form.received_at"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注信息" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useOrderStore } from '@/stores/orders'
import { getCustomers } from '@/api/customers'
import { getProcesses } from '@/api/processes'
import { formatCurrency, unitMap } from '@/utils/format'

const props = defineProps({
  visible: Boolean,
  order: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'saved'])

const store = useOrderStore()
const formRef = ref(null)
const submitting = ref(false)
const isEdit = ref(false)

const customerOptions = ref([])
const processOptions = ref([])
const selectedProcess = ref(null)

const form = reactive({
  customer: null,
  plating_process: null,
  product_name: '',
  product_spec: '',
  quantity: 0,
  unit: '',
  unit_price: 0,
  received_at: '',
  remark: '',
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  plating_process: [{ required: true, message: '请选择镀种工艺', trigger: 'change' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  received_at: [{ required: true, message: '请选择来料日期', trigger: 'change' }],
}

const unitLabel = computed(() => {
  if (!form.unit) return ''
  return unitMap[form.unit] || form.unit
})

const totalAmount = computed(() => {
  const qty = Number(form.quantity) || 0
  const price = Number(form.unit_price) || 0
  return qty * price
})

function getTodayStr() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function loadOptions() {
  try {
    const [custRes, procRes] = await Promise.all([
      getCustomers({ page_size: 200 }),
      getProcesses({ is_active: true, page_size: 200 }),
    ])
    customerOptions.value = custRes.data.results
    processOptions.value = procRes.data.results
  } catch {
    // Handled by interceptor
  }
}

function handleProcessChange(processId) {
  const proc = processOptions.value.find((p) => p.id === processId)
  if (proc) {
    selectedProcess.value = proc
    form.unit = proc.unit
    // Auto-fill base price if unit_price is not set yet
    if (!form.unit_price && proc.base_price) {
      form.unit_price = Number(proc.base_price)
    }
  }
}

function resetForm() {
  isEdit.value = false
  Object.assign(form, {
    customer: null,
    plating_process: null,
    product_name: '',
    product_spec: '',
    quantity: 0,
    unit: '',
    unit_price: 0,
    received_at: getTodayStr(),
    remark: '',
  })
  selectedProcess.value = null
  formRef.value?.clearValidate()
}

function handleOpen() {
  loadOptions()
  if (props.order) {
    isEdit.value = true
    Object.assign(form, {
      customer: props.order.customer,
      plating_process: props.order.plating_process,
      product_name: props.order.product_name,
      product_spec: props.order.product_spec || '',
      quantity: Number(props.order.quantity),
      unit: props.order.unit || '',
      unit_price: Number(props.order.unit_price),
      received_at: props.order.received_at || getTodayStr(),
      remark: props.order.remark || '',
    })
  } else {
    resetForm()
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await store.editOrder(props.order.id, payload)
      ElMessage.success('更新成功')
    } else {
      await store.addOrder(payload)
      ElMessage.success('创建成功')
    }
    emit('update:visible', false)
    emit('saved')
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}

watch(() => props.visible, (val) => {
  if (!val) {
    // reset after close animation
    setTimeout(resetForm, 300)
  }
})
</script>

<style scoped>
.total-amount {
  font-size: 18px;
  font-weight: bold;
  color: #e6a23c;
}
</style>
