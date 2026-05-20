<template>
  <div class="cost-form-dialog">
    <el-dialog
      :model-value="visible"
      :title="isEdit ? '编辑成本' : '录入成本'"
      width="520px"
      :close-on-click-modal="false"
      @update:model-value="$emit('update:visible', $event)"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="90px"
      >
        <el-form-item v-if="!isEdit" label="订单" prop="order">
          <el-select
            v-model="form.order"
            placeholder="选择订单"
            filterable
            style="width: 100%"
            @change="onOrderChange"
          >
            <el-option
              v-for="o in orderOptions"
              :key="o.id"
              :value="o.id"
              :label="`${o.order_no}  ${o.product_name}`"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="订单号">
          <el-input :value="costData?.order_no" disabled />
        </el-form-item>

        <el-form-item v-if="selectedOrder || isEdit" label="订单金额">
          <el-input
            :value="formatCurrency(isEdit ? costData?.order_amount : selectedOrder?.amount)"
            disabled
          />
        </el-form-item>

        <el-form-item label="材料费" prop="material_cost">
          <el-input-number
            v-model="form.material_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="0.00"
            @change="calcTotal"
          />
        </el-form-item>
        <el-form-item label="电费" prop="electricity_cost">
          <el-input-number
            v-model="form.electricity_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="0.00"
            @change="calcTotal"
          />
        </el-form-item>
        <el-form-item label="人工费" prop="labor_cost">
          <el-input-number
            v-model="form.labor_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="0.00"
            @change="calcTotal"
          />
        </el-form-item>
        <el-form-item label="其他费用" prop="other_cost">
          <el-input-number
            v-model="form.other_cost"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="0.00"
            @change="calcTotal"
          />
        </el-form-item>

        <el-divider />

        <el-form-item label="总成本">
          <span class="computed-value">{{ formatCurrency(computedTotal) }}</span>
        </el-form-item>
        <el-form-item label="预计利润">
          <span :class="computedProfit >= 0 ? 'profit-positive' : 'profit-negative'">
            {{ formatCurrency(computedProfit) }}
            <span v-if="computedProfitRate !== null" class="profit-rate">
              ({{ computedProfitRate.toFixed(1) }}%)
            </span>
          </span>
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
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrders } from '@/api/orders'
import { createCost, updateCost } from '@/api/costing'
import { formatCurrency } from '@/utils/format'

const props = defineProps({
  visible: { type: Boolean, default: false },
  costData: { type: Object, default: null }, // null = create, object = edit
})

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = computed(() => !!props.costData)

const formRef = ref(null)
const saving = ref(false)
const orderOptions = ref([])
const selectedOrder = ref(null)

const form = ref({
  order: null,
  material_cost: 0,
  electricity_cost: 0,
  labor_cost: 0,
  other_cost: 0,
  remark: '',
})

const rules = {
  order: [{ required: true, message: '请选择订单', trigger: 'change' }],
}

const computedTotal = computed(() => {
  return (
    (form.value.material_cost || 0) +
    (form.value.electricity_cost || 0) +
    (form.value.labor_cost || 0) +
    (form.value.other_cost || 0)
  )
})

const computedProfit = computed(() => {
  const orderAmt = isEdit.value
    ? Number(props.costData?.order_amount || 0)
    : Number(selectedOrder.value?.amount || 0)
  return orderAmt - computedTotal.value
})

const computedProfitRate = computed(() => {
  const orderAmt = isEdit.value
    ? Number(props.costData?.order_amount || 0)
    : Number(selectedOrder.value?.amount || 0)
  if (!orderAmt) return null
  return (computedProfit.value / orderAmt) * 100
})

function calcTotal() {
  // reactive auto-computed, nothing to do manually
}

function onOrderChange(id) {
  selectedOrder.value = orderOptions.value.find((o) => o.id === id) || null
}

async function loadOrders() {
  try {
    // Load orders without cost entry (completed orders)
    const { data } = await getOrders({ page_size: 500, no_cost: true })
    orderOptions.value = data.results
  } catch {
    // handled by interceptor
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      if (isEdit.value && props.costData) {
        form.value = {
          order: props.costData.order,
          material_cost: Number(props.costData.material_cost) || 0,
          electricity_cost: Number(props.costData.electricity_cost) || 0,
          labor_cost: Number(props.costData.labor_cost) || 0,
          other_cost: Number(props.costData.other_cost) || 0,
          remark: props.costData.remark || '',
        }
      } else {
        resetForm()
        loadOrders()
      }
    }
  }
)

function resetForm() {
  form.value = {
    order: null,
    material_cost: 0,
    electricity_cost: 0,
    labor_cost: 0,
    other_cost: 0,
    remark: '',
  }
  selectedOrder.value = null
  formRef.value?.resetFields()
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = {
        material_cost: form.value.material_cost || 0,
        electricity_cost: form.value.electricity_cost || 0,
        labor_cost: form.value.labor_cost || 0,
        other_cost: form.value.other_cost || 0,
        remark: form.value.remark,
      }
      if (isEdit.value) {
        await updateCost(props.costData.id, payload)
        ElMessage.success('成本更新成功')
      } else {
        await createCost({ ...payload, order: form.value.order })
        ElMessage.success('成本录入成功')
      }
      emit('update:visible', false)
      emit('saved')
    } catch {
      // handled by interceptor
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped>
.computed-value {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.profit-positive {
  font-size: 15px;
  font-weight: 600;
  color: #67c23a;
}
.profit-negative {
  font-size: 15px;
  font-weight: 600;
  color: #f56c6c;
}
.profit-rate {
  font-size: 13px;
  font-weight: normal;
  margin-left: 4px;
}
</style>
