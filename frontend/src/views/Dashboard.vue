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

    <!-- 图表行 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">近6个月收入/利润趋势</span>
          </template>
          <div v-loading="trendLoading" ref="trendChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">客户应收 TOP5</span>
          </template>
          <div v-loading="analysisLoading" ref="customerChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近期订单 -->
    <el-row>
      <el-col :span="24">
        <el-card shadow="hover">
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
import * as echarts from 'echarts'
import { ref, onMounted, onUnmounted } from 'vue'
import { getDashboard, getRevenueTrend, getCustomerAnalysis } from '@/api/reports'
import { getOrders } from '@/api/orders'
import { formatCurrency, orderStatusMap } from '@/utils/format'

// ── State ────────────────────────────────────────────────────────────────────

const dashboard = ref({
  monthly_revenue: 0,
  monthly_expense: 0,
  monthly_profit: 0,
  receivable_balance: 0,
  revenue_change_rate: null,
})

const trendLoading = ref(false)
const analysisLoading = ref(false)
const ordersLoading = ref(false)
const recentOrders = ref([])

// ── Chart refs & instances ────────────────────────────────────────────────────

const trendChartRef = ref(null)
const customerChartRef = ref(null)
let trendChart = null
let customerChart = null

// ── Chart renderers ───────────────────────────────────────────────────────────

function renderTrendChart(data) {
  if (!trendChart) return
  if (!data.length) {
    trendChart.clear()
    return
  }
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        let result = params[0].name + '<br/>'
        params.forEach(p => {
          result += `${p.marker} ${p.seriesName}: ¥${Number(p.value).toLocaleString()}<br/>`
        })
        return result
      },
    },
    legend: {
      data: ['收入', '利润'],
      top: 10,
    },
    grid: {
      left: '3%', right: '4%', bottom: '3%', containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.month),
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: val => val >= 10000 ? (val / 10000) + '万' : val,
      },
    },
    series: [
      {
        name: '收入',
        type: 'line',
        smooth: true,
        data: data.map(d => d.revenue),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ]),
        },
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 2 },
      },
      {
        name: '利润',
        type: 'line',
        smooth: true,
        data: data.map(d => d.profit),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' },
          ]),
        },
        itemStyle: { color: '#67C23A' },
        lineStyle: { width: 2 },
      },
    ],
  }
  trendChart.setOption(option)
}

function renderCustomerChart(data) {
  if (!customerChart) return
  if (!data.length) {
    customerChart.clear()
    return
  }
  // Sort desc, take top 5, then reverse so largest is at top of horizontal bar
  const top5 = [...data]
    .sort((a, b) => Number(b.outstanding_balance) - Number(a.outstanding_balance))
    .slice(0, 5)
    .reverse()

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: params =>
        `${params[0].name}<br/>应收余额: ¥${Number(params[0].value).toLocaleString()}`,
    },
    grid: {
      left: '3%', right: '10%', bottom: '3%', containLabel: true,
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: val => val >= 10000 ? (val / 10000) + '万' : val,
      },
    },
    yAxis: {
      type: 'category',
      data: top5.map(d => d.customer_name),
      axisLabel: {
        overflow: 'truncate',
        width: 80,
      },
    },
    series: [
      {
        type: 'bar',
        data: top5.map(d => d.outstanding_balance),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#E6A23C' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: params =>
            Number(params.value) >= 10000
              ? (Number(params.value) / 10000).toFixed(1) + '万'
              : params.value,
          fontSize: 11,
          color: '#606266',
        },
      },
    ],
  }
  customerChart.setOption(option)
}

// ── Resize handler ────────────────────────────────────────────────────────────

function handleResize() {
  trendChart?.resize()
  customerChart?.resize()
}

// ── Data loaders ──────────────────────────────────────────────────────────────

function changeClass(rate) {
  if (rate == null) return ''
  return rate >= 0 ? 'change-up' : 'change-down'
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
    renderTrendChart(data)
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
    renderCustomerChart(data)
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

// ── Lifecycle ─────────────────────────────────────────────────────────────────

onMounted(() => {
  trendChart = echarts.init(trendChartRef.value)
  customerChart = echarts.init(customerChartRef.value)
  window.addEventListener('resize', handleResize)

  loadDashboard()
  loadTrend()
  loadCustomerAnalysis()
  loadRecentOrders()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  customerChart?.dispose()
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

/* Stat cards */
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
  min-height: 18px;
}
.change-up   { color: #67c23a; }
.change-down { color: #f56c6c; }
.profit-pos  { color: #67c23a; }
.profit-neg  { color: #f56c6c; }
.text-warning { color: #e6a23c; }
.text-success { color: #67c23a; }
.text-danger  { color: #f56c6c; }

.card-title {
  font-weight: 600;
  font-size: 15px;
}
</style>
