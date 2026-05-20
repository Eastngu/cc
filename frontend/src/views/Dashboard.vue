<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>经营看板</h2>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">本月收入</div>
          <div class="stat-value">{{ formatCurrency(dashboard.monthly_revenue) }}</div>
          <div class="stat-change" :class="changeClass(dashboard.revenue_change_rate)">
            <span v-if="dashboard.revenue_change_rate != null">
              {{ dashboard.revenue_change_rate >= 0 ? '▲' : '▼' }}
              {{ Math.abs(dashboard.revenue_change_rate).toFixed(1) }}% 较上月
            </span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">本月支出</div>
          <div class="stat-value">{{ formatCurrency(dashboard.monthly_expense) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">本月利润</div>
          <div
            class="stat-value"
            :class="Number(dashboard.monthly_profit) >= 0 ? 'profit-pos' : 'profit-neg'"
          >
            {{ formatCurrency(dashboard.monthly_profit) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">应收余额</div>
          <div class="stat-value text-warning">{{ formatCurrency(dashboard.receivable_balance) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近6个月趋势 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">近6个月收支趋势</span>
          </template>
          <el-table
            v-loading="trendLoading"
            :data="trendData"
            size="small"
            stripe
          >
            <el-table-column prop="month" label="月份" width="120" align="center" />
            <el-table-column label="营收" align="right">
              <template #default="{ row }">
                {{ formatCurrency(row.revenue) }}
              </template>
            </el-table-column>
            <el-table-column label="成本" align="right">
              <template #default="{ row }">
                {{ formatCurrency(row.cost) }}
              </template>
            </el-table-column>
            <el-table-column label="利润" align="right">
              <template #default="{ row }">
                <span :class="Number(row.profit) >= 0 ? 'text-success' : 'text-danger'">
                  {{ formatCurrency(row.profit) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="利润率" width="100" align="center">
              <template #default="{ row }">
                <span v-if="Number(row.revenue) > 0" :class="getProfitRateClass(row.profit, row.revenue)">
                  {{ ((Number(row.profit) / Number(row.revenue)) * 100).toFixed(1) }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 客户应收 + 近期订单 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">客户应收 TOP5</span>
          </template>
          <el-table
            v-loading="analysisLoading"
            :data="top5Customers"
            size="small"
            stripe
          >
            <el-table-column prop="customer_name" label="客户" min-width="120" />
            <el-table-column label="应收余额" align="right">
              <template #default="{ row }">
                <span class="text-danger">{{ formatCurrency(row.outstanding_balance) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="回款率" width="90" align="center">
              <template #default="{ row }">
                {{ row.collection_rate != null ? `${Number(row.collection_rate).toFixed(1)}%` : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="订单数" width="70" align="center" prop="order_count" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">近期订单</span>
          </template>
          <el-table
            v-loading="ordersLoading"
            :data="recentOrders"
            size="small"
            stripe
          >
            <el-table-column prop="order_no" label="订单号" width="140" />
            <el-table-column prop="customer_name" label="客户" min-width="100" />
            <el-table-column label="金额" align="right" width="110">
              <template #default="{ row }">
                {{ formatCurrency(row.amount) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="orderStatusMap[row.status]?.type" size="small">
                  {{ orderStatusMap[row.status]?.label || row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard, getRevenueTrend, getCustomerAnalysis } from '@/api/reports'
import { getOrders } from '@/api/orders'
import { formatCurrency, orderStatusMap } from '@/utils/format'

const dashboard = ref({
  monthly_revenue: 0,
  monthly_expense: 0,
  monthly_profit: 0,
  receivable_balance: 0,
  revenue_change_rate: null,
})

const trendData = ref([])
const trendLoading = ref(false)

const top5Customers = ref([])
const analysisLoading = ref(false)

const recentOrders = ref([])
const ordersLoading = ref(false)

function changeClass(rate) {
  if (rate == null) return ''
  return rate >= 0 ? 'change-up' : 'change-down'
}

function getProfitRateClass(profit, revenue) {
  const rate = (Number(profit) / Number(revenue)) * 100
  if (rate >= 30) return 'text-success'
  if (rate < 10) return 'text-danger'
  return ''
}

async function loadDashboard() {
  try {
    const { data } = await getDashboard()
    dashboard.value = data
  } catch {
    // handled by interceptor
  }
}

async function loadTrend() {
  trendLoading.value = true
  try {
    const { data } = await getRevenueTrend()
    trendData.value = data
  } catch {
    // handled by interceptor
  } finally {
    trendLoading.value = false
  }
}

async function loadCustomerAnalysis() {
  analysisLoading.value = true
  try {
    const { data } = await getCustomerAnalysis()
    // Sort by outstanding_balance desc, take top 5
    top5Customers.value = [...data]
      .sort((a, b) => Number(b.outstanding_balance) - Number(a.outstanding_balance))
      .slice(0, 5)
  } catch {
    // handled by interceptor
  } finally {
    analysisLoading.value = false
  }
}

async function loadRecentOrders() {
  ordersLoading.value = true
  try {
    const { data } = await getOrders({ page_size: 5 })
    recentOrders.value = data.results
  } catch {
    // handled by interceptor
  } finally {
    ordersLoading.value = false
  }
}

onMounted(() => {
  loadDashboard()
  loadTrend()
  loadCustomerAnalysis()
  loadRecentOrders()
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
.stat-card {
  text-align: center;
  padding: 8px 0;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}
.stat-change {
  font-size: 12px;
  margin-top: 6px;
}
.change-up {
  color: #67c23a;
}
.change-down {
  color: #f56c6c;
}
.profit-pos {
  color: #67c23a;
}
.profit-neg {
  color: #f56c6c;
}
.text-warning {
  color: #e6a23c;
}
.text-success {
  color: #67c23a;
}
.text-danger {
  color: #f56c6c;
}
.card-title {
  font-weight: 600;
  font-size: 15px;
}
</style>
