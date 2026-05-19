<template>
  <div class="customer-list">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="handleAdd">新增客户</el-button>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索客户名称/联系人/电话"
          clearable
          style="width: 300px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
        <el-select
          v-model="billingFilter"
          placeholder="计费方式"
          clearable
          style="width: 150px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option value="area" label="按面积" />
          <el-option value="weight" label="按重量" />
          <el-option value="piece" label="按件数" />
        </el-select>
      </div>

      <el-table
        v-loading="store.loading"
        :data="store.customers"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="short_name" label="简称" width="120" />
        <el-table-column prop="name" label="公司名称" min-width="200" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="payment_terms" label="月结天数" width="100" align="center">
          <template #default="{ row }">{{ row.payment_terms }}天</template>
        </el-table-column>
        <el-table-column prop="default_billing_type" label="计费方式" width="120">
          <template #default="{ row }">
            {{ billingTypeMap[row.default_billing_type] }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确认删除该客户？"
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
        v-if="store.total > 20"
        class="pagination"
        layout="total, prev, pager, next"
        :total="store.total"
        :page-size="20"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </el-card>

    <CustomerForm
      v-model:visible="formVisible"
      :customer="editingCustomer"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCustomerStore } from '@/stores/customers'
import { billingTypeMap } from '@/utils/format'
import CustomerForm from './CustomerForm.vue'

const store = useCustomerStore()
const searchQuery = ref('')
const billingFilter = ref('')
const currentPage = ref(1)
const formVisible = ref(false)
const editingCustomer = ref(null)

function loadData() {
  const params = { page: currentPage.value }
  if (searchQuery.value) params.search = searchQuery.value
  if (billingFilter.value) params.default_billing_type = billingFilter.value
  store.fetchCustomers(params)
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
  editingCustomer.value = null
  formVisible.value = true
}

function handleEdit(row) {
  editingCustomer.value = { ...row }
  formVisible.value = true
}

async function handleDelete(row) {
  await store.removeCustomer(row.id)
  ElMessage.success('删除成功')
  loadData()
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
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
