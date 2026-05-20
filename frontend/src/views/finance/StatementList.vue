<template>
  <div class="statement-list">
    <div class="page-header">
      <h2>月度对账单</h2>
      <el-button type="primary" @click="showGenerateDialog">生成对账单</el-button>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-select
          v-model="customerFilter"
          placeholder="选择客户"
          clearable
          filterable
          style="width: 180px"
          @change="handleSearch"
        >
          <el-option
            v-for="c in customerOptions"
            :key="c.id"
            :value="c.id"
            :label="c.short_name || c.name"
          />
        </el-select>

        <el-select
          v-model="statusFilter"
          placeholder="状态"
          clearable
          style="width: 130px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="(val, key) in statementStatusMap"
            :key="key"
            :value="key"
            :label="val.label"
          />
        </el-select>

        <el-date-picker
          v-model="monthFilter"
          type="month"
          placeholder="选择账期"
          value-format="YYYY-MM"
          style="width: 150px; margin-left: 12px"
          @change="handleSearch"
        />
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="statement_no" label="对账单号" width="170" />
        <el-table-column prop="customer_name" label="客户" width="140" />
        <el-table-column label="账期" width="100" align="center">
          <template #default="{ row }">
            {{ row.year }}-{{ String(row.month).padStart(2, '0') }}
          </template>
        </el-table-column>
        <el-table-column label="合计金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="调整金额" width="120" align="right">
          <template #default="{ row }">
            <span :class="Number(row.adjustment) !== 0 ? 'text-warning' : ''">
              {{ formatCurrency(row.adjustment) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="最终金额" width="130" align="right">
          <template #default="{ row }">
            <strong>{{ formatCurrency(row.final_amount) }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statementStatusMap[row.status]?.type" size="small">
              {{ statementStatusMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'draft'"
              link
              type="success"
              @click="handleConfirm(row)"
            >
              确认
            </el-button>
            <el-button link type="primary" @click="handleViewDetail(row)">查看明细</el-button>
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

    <!-- 生成对账单对话框 -->
    <el-dialog
      v-model="generateVisible"
      title="生成对账单"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="generateFormRef"
        :model="generateForm"
        :rules="generateRules"
        label-width="80px"
      >
        <el-form-item label="客户" prop="customer">
          <el-select
            v-model="generateForm.customer"
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
        <el-form-item label="账期" prop="yearMonth">
          <el-date-picker
            v-model="generateForm.yearMonth"
            type="month"
            placeholder="选择年月"
            value-format="YYYY-MM"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateVisible = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">生成</el-button>
      </template>
    </el-dialog>

    <!-- 对账单明细对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="detailTitle"
      width="900px"
    >
      <template v-if="currentStatement">
        <el-descriptions :column="3" border size="small" style="margin-bottom: 20px">
          <el-descriptions-item label="对账单号">{{ currentStatement.statement_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentStatement.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="账期">
            {{ currentStatement.year }}-{{ String(currentStatement.month).padStart(2, '0') }}
          </el-descriptions-item>
          <el-descriptions-item label="合计金额">{{ formatCurrency(currentStatement.total_amount) }}</el-descriptions-item>
          <el-descriptions-item label="调整金额">{{ formatCurrency(currentStatement.adjustment) }}</el-descriptions-item>
          <el-descriptions-item label="最终金额">
            <strong>{{ formatCurrency(currentStatement.final_amount) }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">{{ currentStatement.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-table
          v-loading="detailLoading"
          :data="currentStatement.orders || []"
          size="small"
          stripe
        >
          <el-table-column prop="order_no" label="订单号" width="150" />
          <el-table-column prop="product_name" label="产品" min-width="120" />
          <el-table-column prop="process_name" label="工艺" width="100" />
          <el-table-column label="数量" width="100" align="right">
            <template #default="{ row }">
              {{ row.quantity }} {{ row.unit }}
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120" align="right">
            <template #default="{ row }">
              {{ formatCurrency(row.amount) }}
            </template>
          </el-table-column>
          <el-table-column label="完工日期" width="110" align="center">
            <template #default="{ row }">
              {{ formatDate(row.completed_date) }}
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStatements, getStatement, generateStatement, confirmStatement } from '@/api/statements'
import { getCustomers } from '@/api/customers'
import { formatCurrency, formatDate, statementStatusMap } from '@/utils/format'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const customerFilter = ref(null)
const statusFilter = ref('')
const monthFilter = ref('')

const customerOptions = ref([])

// 生成对账单
const generateVisible = ref(false)
const generating = ref(false)
const generateFormRef = ref(null)
const generateForm = ref({ customer: null, yearMonth: '' })
const generateRules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  yearMonth: [{ required: true, message: '请选择账期', trigger: 'change' }],
}

// 明细
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentStatement = ref(null)
const detailTitle = ref('对账单明细')

async function loadCustomers() {
  try {
    const { data } = await getCustomers({ page_size: 200 })
    customerOptions.value = data.results
  } catch {
    // handled by interceptor
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (customerFilter.value) params.customer = customerFilter.value
    if (statusFilter.value) params.status = statusFilter.value
    if (monthFilter.value) {
      const [y, m] = monthFilter.value.split('-')
      params.year = y
      params.month = Number(m)
    }
    const { data } = await getStatements(params)
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

function showGenerateDialog() {
  generateForm.value = { customer: null, yearMonth: '' }
  generateVisible.value = true
}

async function handleGenerate() {
  if (!generateFormRef.value) return
  await generateFormRef.value.validate(async (valid) => {
    if (!valid) return
    generating.value = true
    try {
      const [year, month] = generateForm.value.yearMonth.split('-')
      await generateStatement({
        customer: generateForm.value.customer,
        year: Number(year),
        month: Number(month),
      })
      ElMessage.success('对账单生成成功')
      generateVisible.value = false
      loadData()
    } catch {
      // handled by interceptor
    } finally {
      generating.value = false
    }
  })
}

async function handleConfirm(row) {
  try {
    await ElMessageBox.confirm(
      `确认对账单 ${row.statement_no}？确认后不可修改。`,
      '提示',
      { type: 'warning' }
    )
    await confirmStatement(row.id)
    ElMessage.success('已确认')
    loadData()
  } catch {
    // user cancelled or interceptor handled
  }
}

async function handleViewDetail(row) {
  detailTitle.value = `对账单明细 - ${row.statement_no}`
  currentStatement.value = row
  detailVisible.value = true
  detailLoading.value = true
  try {
    const { data } = await getStatement(row.id)
    currentStatement.value = data
  } catch {
    // handled by interceptor
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  loadCustomers()
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
  gap: 0;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.text-warning {
  color: #e6a23c;
  font-weight: 500;
}
</style>
