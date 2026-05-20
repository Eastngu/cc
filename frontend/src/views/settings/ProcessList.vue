<template>
  <div class="process-list">
    <div class="page-header">
      <h2>工艺配置</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增工艺</el-button>
    </div>

    <el-card>
      <el-table
        v-loading="tableLoading"
        :data="processes"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column label="计费单位" width="130">
          <template #default="{ row }">
            {{ billingTypeMap[row.unit] || row.unit }}
          </template>
        </el-table-column>
        <el-table-column label="基础单价" width="130" align="right">
          <template #default="{ row }">
            {{ formatCurrency(row.base_price) }}
          </template>
        </el-table-column>
        <el-table-column label="描述" min-width="180">
          <template #default="{ row }">
            {{ row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确认删除该工艺？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create / Edit dialog -->
    <el-dialog
      :title="editingProcess ? '编辑工艺' : '新增工艺'"
      v-model="dialogVisible"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="工艺名称" prop="name">
          <el-input v-model="form.name" placeholder="如: 镀镍" />
        </el-form-item>
        <el-form-item label="工艺编码" prop="code">
          <el-input v-model="form.code" placeholder="如: Ni" />
        </el-form-item>
        <el-form-item label="计费单位" prop="unit">
          <el-select v-model="form.unit" style="width: 100%">
            <el-option value="area" label="面积 (dm²)" />
            <el-option value="weight" label="重量 (kg)" />
            <el-option value="piece" label="件数 (件)" />
          </el-select>
        </el-form-item>
        <el-form-item label="基础单价" prop="base_price">
          <el-input-number
            v-model="form.base_price"
            :min="0"
            :precision="4"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.is_active"
            active-text="启用"
            inactive-text="停用"
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
  getProcesses,
  createProcess,
  updateProcess,
  deleteProcess,
} from '@/api/processes'
import { formatCurrency, billingTypeMap } from '@/utils/format'

const processes = ref([])
const tableLoading = ref(false)
const dialogVisible = ref(false)
const editingProcess = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '',
  code: '',
  unit: 'area',
  base_price: 0,
  description: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入工艺名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入工艺编码', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择计费单位', trigger: 'change' }],
  base_price: [{ required: true, message: '请输入基础单价', trigger: 'blur' }],
}

async function loadProcesses() {
  tableLoading.value = true
  try {
    const { data } = await getProcesses({ page_size: 200 })
    processes.value = data.results
  } finally {
    tableLoading.value = false
  }
}

function resetForm() {
  editingProcess.value = null
  Object.assign(form, {
    name: '',
    code: '',
    unit: 'area',
    base_price: 0,
    description: '',
    is_active: true,
  })
  formRef.value?.clearValidate()
}

function handleAdd() {
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  editingProcess.value = row
  Object.assign(form, {
    name: row.name,
    code: row.code,
    unit: row.unit,
    base_price: Number(row.base_price),
    description: row.description || '',
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await deleteProcess(row.id)
    ElMessage.success('删除成功')
    loadProcesses()
  } catch {
    // Handled by interceptor
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingProcess.value) {
      await updateProcess(editingProcess.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await createProcess(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProcesses()
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProcesses()
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
</style>
