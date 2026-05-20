<template>
  <div class="order-list">
    <div class="page-header">
      <h2>订单管理</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新建订单</el-button>
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
          placeholder="订单状态"
          clearable
          style="width: 140px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option
            v-for="(val, key) in orderStatusMap"
            :key="key"
            :value="key"
            :label="val.label"
          />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="来料开始"
          end-placeholder="来料结束"
          value-format="YYYY-MM-DD"
          style="margin-left: 12px; width: 240px"
          @change="handleSearch"
        />

        <el-input
          v-model="searchQuery"
          placeholder="搜索订单号/产品名称"
          clearable
          style="width: 220px; margin-left: 12px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>

      <el-table
        v-loading="store.loading"
        :data="store.orders"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="order_no" label="订单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="130" />
        <el-table-column prop="product_name" label="产品名称" min-width="160" />
        <el-table-column prop="process_name" label="镀种" width="120" />
        <el-table-column label="数量" width="110" align="right">
          <template #default="{ row }">
            {{ row.quantity }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="orderStatusMap[row.status]?.type" size="small">
              {{ orderStatusMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来料日期" width="110" align="center">
          <template #default="{ row }">
            {{ formatDate(row.received_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="warning" @click="handleStatusChange(row)">变更状态</el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="primary"
              @click="handleEdit(row)"
            >编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="store.total > 0"
        class="pagination"
        layout="total, prev, pager, next"
        :total="store.total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- Order form dialog -->
    <OrderForm
      v-model:visible="formVisible"
      :order="editingOrder"
      @saved="loadData"
    />

    <!-- View detail dialog -->
    <el-dialog v-model="viewVisible" title="订单详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ viewOrder?.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="orderStatusMap[viewOrder?.status]?.type" size="small">
            {{ orderStatusMap[viewOrder?.status]?.label }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户">{{ viewOrder?.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="镀种">{{ viewOrder?.process_name }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ viewOrder?.product_name }}</el-descriptions-item>
        <el-descriptions-item label="产品规格">{{ viewOrder?.product_spec || '-' }}</el-descriptions-item>
        <el-descriptions-item label="数量">
          {{ viewOrder?.quantity }} {{ viewOrder?.unit }}
        </el-descriptions-item>
        <el-descriptions-item label="单价">
          {{ formatCurrency(viewOrder?.unit_price) }}
        </el-descriptions-item>
        <el-descriptions-item label="金额">
          {{ formatCurrency(viewOrder?.total_amount) }}
        </el-descriptions-item>
        <el-descriptions-item label="来料日期">
          {{ formatDate(viewOrder?.received_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="完工日期">
          {{ formatDate(viewOrder?.completed_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="出货日期">
          {{ formatDate(viewOrder?.shipped_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ viewOrder?.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Status change dialog -->
    <el-dialog v-model="statusVisible" title="变更订单状态" width="360px">
      <el-form label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="orderStatusMap[statusOrder?.status]?.type" size="small">
            {{ orderStatusMap[statusOrder?.status]?.label }}
          </el-tag>
        </el-form-item>
        <el-form-item label="变更为">
          <el-radio-group v-model="newStatus">
            <el-radio
              v-for="(val, key) in orderStatusMap"
              :key="key"
              :value="key"
              :disabled="key === statusOrder?.status"
              style="display: block; margin-bottom: 8px"
            >
              {{ val.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusVisible = false">取消</el-button>
        <el-button type="primary" :loading="statusSubmitting" @click="confirmStatusChange">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useOrderStore } from '@/stores/orders'
import { getCustomers } from '@/api/customers'
import { formatCurrency, formatDate, orderStatusMap } from '@/utils/format'
import OrderForm from './OrderForm.vue'

const store = useOrderStore()
const searchQuery = ref('')
const customerFilter = ref(null)
const statusFilter = ref('')
const dateRange = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)

const formVisible = ref(false)
const editingOrder = ref(null)

const viewVisible = ref(false)
const viewOrder = ref(null)

const statusVisible = ref(false)
const statusOrder = ref(null)
const newStatus = ref('')
const statusSubmitting = ref(false)

const customerOptions = ref([])

async function loadCustomers() {
  try {
    const { data } = await getCustomers({ page_size: 200 })
    customerOptions.value = data.results
  } catch {
    // silently fail
  }
}

function loadData() {
  const params = { page: currentPage.value, page_size: pageSize.value }
  if (searchQuery.value) params.search = searchQuery.value
  if (customerFilter.value) params.customer = customerFilter.value
  if (statusFilter.value) params.status = statusFilter.value
  if (dateRange.value?.[0]) params.received_at_after = dateRange.value[0]
  if (dateRange.value?.[1]) params.received_at_before = dateRange.value[1]
  store.fetchOrders(params)
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
  editingOrder.value = null
  formVisible.value = true
}

function handleEdit(row) {
  editingOrder.value = { ...row }
  formVisible.value = true
}

function handleView(row) {
  viewOrder.value = row
  viewVisible.value = true
}

function handleStatusChange(row) {
  statusOrder.value = row
  newStatus.value = row.status
  statusVisible.value = true
}

async function confirmStatusChange() {
  if (!newStatus.value || newStatus.value === statusOrder.value.status) {
    ElMessage.warning('请选择不同的状态')
    return
  }
  statusSubmitting.value = true
  try {
    await store.updateStatus(statusOrder.value.id, newStatus.value)
    ElMessage.success('状态更新成功')
    statusVisible.value = false
    loadData()
  } catch {
    // Handled by interceptor
  } finally {
    statusSubmitting.value = false
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
</style>
