<template>
  <div class="payable-list">
    <div class="page-header">
      <h2>应付账款</h2>
      <el-button type="primary" @click="handleAdd">新建应付</el-button>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-select
          v-model="statusFilter"
          placeholder="账款状态"
          clearable
          style="width: 140px"
          @change="handleSearch"
        >
          <el-option
            v-for="(val, key) in payableStatusMap"
            :key="key"
            :value="key"
            :label="val.label"
          />
        </el-select>

        <el-select
          v-model="categoryFilter"
          placeholder="类别"
          clearable
          style="width: 130px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="(label, key) in payableCategoryMap"
            :key="key"
            :value="key"
            :label="label"
          />
        </el-select>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="payable_no" label="应付单号" width="160" />
        <el-table-column prop="supplier_name" label="供应商" min-width="140" />
        <el-table-column label="类别" width="100" align="center">
          <template #default="{ row }">
            {{ payableCategoryMap[row.category] || row.category_display }}
          </template>
        </el-table-column>
        <el-table-column label="应付金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="已付金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.paid_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="余额" width="130" align="right">
          <template #default="{ row }">
            <span :class="Number(row.balance) > 0 ? 'text-danger' : ''">
              {{ formatCurrency(row.balance) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="payableStatusMap[row.status]?.type" size="small">
              {{ payableStatusMap[row.status]?.label || row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120">
          <template #default="{ row }">
            {{ row.remark || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'settled'"
              link
              type="primary"
              @click="handlePay(row)"
            >
              付款
            </el-button>
            <span v-else class="settled-text">已结清</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        class="pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- Create payable dialog -->
    <el-dialog
      v-model="createVisible"
      title="新建应付账款"
      width="480px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="90px"
      >
        <el-form-item label="供应商" prop="supplier_name">
          <el-input v-model="createForm.supplier_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-select v-model="createForm.category" placeholder="请选择类别" style="width: 100%">
            <el-option
              v-for="(label, key) in payableCategoryMap"
              :key="key"
              :value="key"
              :label="label"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="应付金额" prop="total_amount">
          <el-input-number
            v-model="createForm.total_amount"
            :min="0.01"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="到期日" prop="due_date">
          <el-date-picker
            v-model="createForm.due_date"
            type="date"
            placeholder="选择到期日"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="createForm.remark"
            type="textarea"
            :rows="2"
            placeholder="备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Payment form dialog -->
    <PaymentForm
      v-model:visible="paymentVisible"
      type="pay"
      :preset-payable="presetPayable"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPayables, createPayable } from '@/api/finance'
import { formatCurrency, formatDate, payableStatusMap, payableCategoryMap } from '@/utils/format'
import PaymentForm from './PaymentForm.vue'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const statusFilter = ref('')
const categoryFilter = ref('')

// create payable
const createVisible = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  supplier_name: '',
  category: '',
  total_amount: 0,
  due_date: '',
  remark: '',
})
const createRules = {
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
  total_amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    {
      validator: (_, value, cb) => {
        if (!value || value <= 0) cb(new Error('金额必须大于0'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
  due_date: [{ required: true, message: '请选择到期日', trigger: 'change' }],
}

// payment form
const paymentVisible = ref(false)
const presetPayable = ref(null)

async function loadData() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (statusFilter.value) params.status = statusFilter.value
    if (categoryFilter.value) params.category = categoryFilter.value
    const { data } = await getPayables(params)
    list.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadData()
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

function handleAdd() {
  createVisible.value = true
}

function resetCreateForm() {
  Object.assign(createForm, {
    supplier_name: '',
    category: '',
    total_amount: 0,
    due_date: '',
    remark: '',
  })
  createFormRef.value?.clearValidate()
}

async function handleCreateSubmit() {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  creating.value = true
  try {
    await createPayable({ ...createForm })
    ElMessage.success('创建成功')
    createVisible.value = false
    loadData()
  } catch {
    // Handled by interceptor
  } finally {
    creating.value = false
  }
}

function handlePay(row) {
  presetPayable.value = row.id
  paymentVisible.value = true
}

onMounted(() => {
  loadData()
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
  flex-wrap: wrap;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.text-danger {
  color: #f56c6c;
  font-weight: 500;
}
.settled-text {
  font-size: 13px;
  color: #909399;
}
</style>
