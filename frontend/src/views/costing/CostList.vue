<template>
  <div class="cost-list">
    <div class="page-header">
      <h2>成本核算</h2>
      <el-button type="primary" @click="handleAdd">录入成本</el-button>
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

        <el-input
          v-model="searchQuery"
          placeholder="搜索订单号"
          clearable
          style="width: 200px; margin-left: 12px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="order_no" label="订单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="130" />
        <el-table-column label="订单金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.order_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="材料费" width="110" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.material_cost) }}
          </template>
        </el-table-column>
        <el-table-column label="电费" width="100" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.electricity_cost) }}
          </template>
        </el-table-column>
        <el-table-column label="人工费" width="100" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.labor_cost) }}
          </template>
        </el-table-column>
        <el-table-column label="其他" width="100" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.other_cost) }}
          </template>
        </el-table-column>
        <el-table-column label="总成本" width="120" align="right">
          <template #default="{ row }">
            <strong>{{ formatCurrency(row.total_cost) }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="利润" width="120" align="right">
          <template #default="{ row }">
            <span :class="Number(row.profit) >= 0 ? 'text-success' : 'text-danger'">
              {{ formatCurrency(row.profit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="利润率" width="100" align="center">
          <template #default="{ row }">
            <span :class="getProfitRateClass(row.profit_rate)">
              {{ formatProfitRate(row.profit_rate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
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

    <CostForm
      v-model:visible="formVisible"
      :cost-data="editingCost"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCosts } from '@/api/costing'
import { getCustomers } from '@/api/customers'
import { formatCurrency } from '@/utils/format'
import CostForm from './CostForm.vue'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const customerFilter = ref(null)
const searchQuery = ref('')

const customerOptions = ref([])
const formVisible = ref(false)
const editingCost = ref(null)

function formatProfitRate(rate) {
  if (rate == null) return '-'
  return `${Number(rate).toFixed(1)}%`
}

function getProfitRateClass(rate) {
  const r = Number(rate)
  if (r >= 30) return 'rate-high'
  if (r < 10) return 'rate-low'
  return ''
}

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
    if (searchQuery.value) params.search = searchQuery.value
    const { data } = await getCosts(params)
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
  editingCost.value = null
  formVisible.value = true
}

function handleEdit(row) {
  editingCost.value = { ...row }
  formVisible.value = true
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
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.text-success {
  color: #67c23a;
  font-weight: 500;
}
.text-danger {
  color: #f56c6c;
  font-weight: 500;
}
.rate-high {
  color: #67c23a;
  font-weight: 600;
}
.rate-low {
  color: #f56c6c;
  font-weight: 600;
}
</style>
