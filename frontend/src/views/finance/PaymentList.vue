<template>
  <div class="payment-list">
    <div class="page-header">
      <h2>收付款记录</h2>
      <div class="header-actions">
        <el-button type="success" @click="handleReceive">登记收款</el-button>
        <el-button type="danger" @click="handlePay">登记付款</el-button>
      </div>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-select
          v-model="typeFilter"
          placeholder="流水类型"
          clearable
          style="width: 130px"
          @change="handleSearch"
        >
          <el-option value="receive" label="收款" />
          <el-option value="pay" label="付款" />
        </el-select>

        <el-select
          v-model="methodFilter"
          placeholder="支付方式"
          clearable
          style="width: 140px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="(label, key) in paymentMethodMap"
            :key="key"
            :value="key"
            :label="label"
          />
        </el-select>

        <el-select
          v-model="customerFilter"
          placeholder="选择客户"
          clearable
          filterable
          style="width: 180px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="c in customerOptions"
            :key="c.id"
            :value="c.id"
            :label="c.short_name || c.name"
          />
        </el-select>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="payment_no" label="流水号" width="160" />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.type === 'receive' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.type === 'receive' ? '收款' : '付款' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="往来方" min-width="140">
          <template #default="{ row }">
            {{ row.customer_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="130" align="right">
          <template #default="{ row }">
            <span :class="row.type === 'receive' ? 'text-success' : 'text-danger'">
              {{ row.type === 'receive' ? '+' : '-' }}{{ formatCurrency(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="支付方式" width="110" align="center">
          <template #default="{ row }">
            {{ paymentMethodMap[row.payment_method] || row.method_display }}
          </template>
        </el-table-column>
        <el-table-column label="日期" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.payment_date) }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="140">
          <template #default="{ row }">
            {{ row.remark || '-' }}
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
      :type="paymentType"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPayments } from '@/api/finance'
import { getCustomers } from '@/api/customers'
import { formatCurrency, formatDate, paymentMethodMap } from '@/utils/format'
import PaymentForm from './PaymentForm.vue'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const typeFilter = ref('')
const methodFilter = ref('')
const customerFilter = ref(null)

const customerOptions = ref([])

const paymentVisible = ref(false)
const paymentType = ref('receive')

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
    if (typeFilter.value) params.type = typeFilter.value
    if (methodFilter.value) params.payment_method = methodFilter.value
    if (customerFilter.value) params.customer = customerFilter.value
    const { data } = await getPayments(params)
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

function handleReceive() {
  paymentType.value = 'receive'
  paymentVisible.value = true
}

function handlePay() {
  paymentType.value = 'pay'
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
.header-actions {
  display: flex;
  gap: 8px;
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
</style>
