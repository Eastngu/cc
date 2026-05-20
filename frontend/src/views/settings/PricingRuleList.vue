<template>
  <div class="pricing-rule-list">
    <div class="page-header">
      <h2>计费规则</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增计费规则</el-button>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-select
          v-model="filterCustomer"
          placeholder="按客户筛选"
          clearable
          style="width: 200px"
          @change="handleSearch"
        >
          <el-option
            v-for="c in customers"
            :key="c.id"
            :label="c.short_name || c.name"
            :value="c.id"
          />
        </el-select>
        <el-select
          v-model="filterProcess"
          placeholder="按工艺筛选"
          clearable
          style="width: 200px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="p in processes"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
      </div>

      <el-table
        v-loading="tableLoading"
        :data="rules"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column label="客户" min-width="140">
          <template #default="{ row }">
            <el-tag v-if="!row.customer_name" type="info" size="small">通用</el-tag>
            <span v-else>{{ row.customer_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="process_name" label="镀种工艺" min-width="140" />
        <el-table-column label="单价" width="120" align="right">
          <template #default="{ row }">
            {{ formatPrice(row.unit_price) }}
          </template>
        </el-table-column>
        <el-table-column label="最低收费" width="120" align="right">
          <template #default="{ row }">
            {{ row.min_charge != null ? formatPrice(row.min_charge) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="effective_date" label="生效日期" width="120" />
        <el-table-column label="备注" min-width="160">
          <template #default="{ row }">
            {{ row.remark || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确认删除该计费规则？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > pageSize"
        class="pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- Create / Edit dialog -->
    <el-dialog
      :title="editingRule ? '编辑计费规则' : '新增计费规则'"
      v-model="dialogVisible"
      width="520px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules_form"
        label-width="100px"
      >
        <el-form-item label="客户" prop="customer">
          <el-select
            v-model="form.customer"
            placeholder="选择客户（不选则为通用规则）"
            clearable
            style="width: 100%"
          >
            <el-option :value="null" label="通用（所有客户）" />
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="c.short_name || c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="镀种工艺" prop="plating_process">
          <el-select
            v-model="form.plating_process"
            placeholder="请选择镀种工艺"
            style="width: 100%"
          >
            <el-option
              v-for="p in processes"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="单价" prop="unit_price">
          <el-input-number
            v-model="form.unit_price"
            :min="0"
            :step="0.01"
            :precision="4"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="最低收费" prop="min_charge">
          <el-input-number
            v-model="form.min_charge"
            :min="0"
            :step="1"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="生效日期" prop="effective_date">
          <el-date-picker
            v-model="form.effective_date"
            type="date"
            placeholder="选择生效日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getPricingRules,
  createPricingRule,
  updatePricingRule,
  deletePricingRule,
} from '@/api/pricing'
import { getCustomers } from '@/api/customers'
import { getProcesses } from '@/api/processes'

const PAGE_SIZE = 20

const rules = ref([])
const total = ref(0)
const pageSize = ref(PAGE_SIZE)
const currentPage = ref(1)
const tableLoading = ref(false)
const dialogVisible = ref(false)
const editingRule = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const filterCustomer = ref(null)
const filterProcess = ref(null)

const customers = ref([])
const processes = ref([])

const form = reactive({
  customer: null,
  plating_process: null,
  unit_price: 0,
  min_charge: 0,
  effective_date: '',
  remark: '',
})

const rules_form = {
  plating_process: [{ required: true, message: '请选择镀种工艺', trigger: 'change' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  effective_date: [{ required: true, message: '请选择生效日期', trigger: 'change' }],
}

function formatPrice(val) {
  if (val == null) return '-'
  return Number(val).toFixed(4)
}

async function loadRules() {
  tableLoading.value = true
  try {
    const params = { page: currentPage.value, page_size: PAGE_SIZE }
    if (filterCustomer.value) params.customer = filterCustomer.value
    if (filterProcess.value) params.plating_process = filterProcess.value
    const { data } = await getPricingRules(params)
    rules.value = data.results
    total.value = data.count
  } finally {
    tableLoading.value = false
  }
}

async function loadOptions() {
  const [custRes, procRes] = await Promise.all([
    getCustomers({ page_size: 500 }),
    getProcesses({ page_size: 500 }),
  ])
  customers.value = custRes.data.results
  processes.value = procRes.data.results
}

function handleSearch() {
  currentPage.value = 1
  loadRules()
}

function handlePageChange(page) {
  currentPage.value = page
  loadRules()
}

function resetForm() {
  editingRule.value = null
  Object.assign(form, {
    customer: null,
    plating_process: null,
    unit_price: 0,
    min_charge: 0,
    effective_date: '',
    remark: '',
  })
  formRef.value?.clearValidate()
}

function handleAdd() {
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  editingRule.value = row
  Object.assign(form, {
    customer: row.customer ?? null,
    plating_process: row.plating_process,
    unit_price: Number(row.unit_price),
    min_charge: row.min_charge != null ? Number(row.min_charge) : 0,
    effective_date: row.effective_date || '',
    remark: row.remark || '',
  })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await deletePricingRule(row.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch {
    // Handled by interceptor
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      customer: form.customer || null,
      plating_process: form.plating_process,
      unit_price: form.unit_price,
      min_charge: form.min_charge,
      effective_date: form.effective_date,
      remark: form.remark,
    }
    if (editingRule.value) {
      await updatePricingRule(editingRule.value.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createPricingRule(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadRules()
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadOptions()
  loadRules()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
}
.filter-bar {
  display: flex;
  align-items: center;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
