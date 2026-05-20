<template>
  <div class="receivable-list">
    <div class="page-header">
      <h2>应收账款</h2>
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
          placeholder="账款状态"
          clearable
          style="width: 140px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="(val, key) in receivableStatusMap"
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
        <el-table-column prop="receivable_no" label="应收单号" width="160" />
        <el-table-column prop="customer_name" label="客户" width="130" />
        <el-table-column label="账期" width="100" align="center">
          <template #default="{ row }">
            {{ row.year }}-{{ String(row.month).padStart(2, '0') }}
          </template>
        </el-table-column>
        <el-table-column label="应收金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="已收金额" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.received_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="余额" width="130" align="right">
          <template #default="{ row }">
            <span :class="Number(row.balance) > 0 ? 'text-danger' : ''">
              {{ formatCurrency(row.balance) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="receivableStatusMap[row.status]?.type" size="small">
              {{ receivableStatusMap[row.status]?.label || row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'settled'"
              link
              type="primary"
              @click="handleCollect(row)"
            >
              收款
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

    <PaymentForm
      v-model:visible="paymentVisible"
      type="receive"
      :preset-customer="presetCustomer"
      :preset-receivable="presetReceivable"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReceivables } from '@/api/finance'
import { getCustomers } from '@/api/customers'
import { formatCurrency, formatDate, receivableStatusMap } from '@/utils/format'
import PaymentForm from './PaymentForm.vue'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const customerFilter = ref(null)
const statusFilter = ref('')
const monthFilter = ref('')

const customerOptions = ref([])

const paymentVisible = ref(false)
const presetCustomer = ref(null)
const presetReceivable = ref(null)

async function loadCustomers() {
  try {
    const { data } = await getCustomers({ page_size: 200 })
    customerOptions.value = data.results
  } catch {
    // Handled by interceptor
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
    const { data } = await getReceivables(params)
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

function handleCollect(row) {
  presetCustomer.value = row.customer
  presetReceivable.value = row.id
  paymentVisible.value = true
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
.text-danger {
  color: #f56c6c;
  font-weight: 500;
}
.settled-text {
  font-size: 13px;
  color: #909399;
}
</style>
