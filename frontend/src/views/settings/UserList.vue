<template>
  <div class="page-container">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增用户</el-button>
    </div>

    <!-- Search bar -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.search" placeholder="用户名/姓名/手机号" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadUsers">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="角色" width="130">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">
              {{ roleName(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="230">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="openResetDialog(row)">重置密码</el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'danger' : 'success'"
              @click="toggleActive(row)"
            >{{ row.is_active ? '禁用' : '启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create dialog -->
    <el-dialog v-model="createDialogVisible" title="新增用户" width="480px" :close-on-click-modal="false">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="createForm.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="createForm.phone" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- Edit dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑用户" width="480px" :close-on-click-modal="false">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="90px">
        <el-form-item label="用户名">
          <el-input :value="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="editForm.real_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- Reset password dialog -->
    <el-dialog v-model="resetDialogVisible" title="重置密码" width="420px" :close-on-click-modal="false">
      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" label-width="90px">
        <el-form-item label="用户">
          <span>{{ resetTarget?.real_name }}（{{ resetTarget?.username }}）</span>
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="resetForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReset">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser, resetPassword } from '@/api/users'

// ---- state ----
const users = ref([])
const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({ search: '', role: '', is_active: '' })

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const resetDialogVisible = ref(false)

const createFormRef = ref(null)
const editFormRef = ref(null)
const resetFormRef = ref(null)

const createForm = reactive({ username: '', password: '', real_name: '', role: 'workshop', phone: '' })
const editForm = reactive({ id: null, username: '', real_name: '', role: 'workshop', phone: '' })
const resetForm = reactive({ password: '' })
const resetTarget = ref(null)

// ---- options ----
const roleOptions = [
  { value: 'boss', label: '老板/管理层' },
  { value: 'finance', label: '财务人员' },
  { value: 'workshop', label: '车间主管' },
]

// ---- rules ----
const createRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}
const editRules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}
const resetRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
}

// ---- helpers ----
function roleTagType(role) {
  return { boss: 'danger', finance: 'warning', workshop: 'info' }[role] || ''
}
function roleName(role) {
  return roleOptions.find(r => r.value === role)?.label || role
}

// ---- data loading ----
async function loadUsers() {
  loading.value = true
  try {
    const params = {}
    if (searchForm.search) params.search = searchForm.search
    if (searchForm.role) params.role = searchForm.role
    if (searchForm.is_active !== '') params.is_active = searchForm.is_active
    const { data } = await getUsers(params)
    users.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  searchForm.search = ''
  searchForm.role = ''
  searchForm.is_active = ''
  loadUsers()
}

// ---- create ----
function openCreateDialog() {
  Object.assign(createForm, { username: '', password: '', real_name: '', role: 'workshop', phone: '' })
  createDialogVisible.value = true
}

async function submitCreate() {
  await createFormRef.value.validate()
  submitting.value = true
  try {
    await createUser({ ...createForm })
    ElMessage.success('用户创建成功')
    createDialogVisible.value = false
    loadUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.username?.[0] || err.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

// ---- edit ----
function openEditDialog(row) {
  Object.assign(editForm, { id: row.id, username: row.username, real_name: row.real_name, role: row.role, phone: row.phone })
  editDialogVisible.value = true
}

async function submitEdit() {
  await editFormRef.value.validate()
  submitting.value = true
  try {
    await updateUser(editForm.id, { real_name: editForm.real_name, role: editForm.role, phone: editForm.phone })
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadUsers()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// ---- reset password ----
function openResetDialog(row) {
  resetTarget.value = row
  resetForm.password = ''
  resetDialogVisible.value = true
}

async function submitReset() {
  await resetFormRef.value.validate()
  submitting.value = true
  try {
    await resetPassword(resetTarget.value.id, resetForm.password)
    ElMessage.success('密码重置成功')
    resetDialogVisible.value = false
  } catch {
    ElMessage.error('重置失败')
  } finally {
    submitting.value = false
  }
}

// ---- toggle active ----
async function toggleActive(row) {
  const action = row.is_active ? '禁用' : '启用'
  await ElMessageBox.confirm(`确定要${action}用户「${row.real_name}」吗？`, '提示', { type: 'warning' })
  try {
    await updateUser(row.id, { is_active: !row.is_active })
    ElMessage.success(`已${action}`)
    loadUsers()
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.page-container {
  padding: 0;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.search-card {
  margin-bottom: 16px;
}
</style>
