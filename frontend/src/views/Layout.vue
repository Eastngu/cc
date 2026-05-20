<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <span v-if="!isCollapse">电镀 ERP</span>
        <span v-else>ERP</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item v-if="hasAccess(['boss', 'finance'])" index="/">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>经营看板</template>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><Document /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>
        <el-sub-menu v-if="hasAccess(['boss', 'finance'])" index="/finance">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/finance/receivables">
            <el-icon><Tickets /></el-icon>
            <template #title>应收账款</template>
          </el-menu-item>
          <el-menu-item index="/finance/payables">
            <el-icon><CreditCard /></el-icon>
            <template #title>应付账款</template>
          </el-menu-item>
          <el-menu-item index="/finance/payments">
            <el-icon><Money /></el-icon>
            <template #title>收付款记录</template>
          </el-menu-item>
          <el-menu-item index="/finance/statements">
            <el-icon><Notebook /></el-icon>
            <template #title>月度对账单</template>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-if="hasAccess(['boss', 'finance'])" index="/costing">
          <el-icon><Coin /></el-icon>
          <template #title>成本核算</template>
        </el-menu-item>
        <el-sub-menu v-if="hasAccess(['boss', 'finance'])" index="/settings">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/customers">
            <el-icon><User /></el-icon>
            <template #title>客户管理</template>
          </el-menu-item>
          <el-menu-item index="/settings/processes">
            <el-icon><Tools /></el-icon>
            <template #title>工艺配置</template>
          </el-menu-item>
          <el-menu-item index="/settings/pricing">
            <el-icon><Money /></el-icon>
            <template #title>计费规则</template>
          </el-menu-item>
          <el-menu-item v-if="hasAccess(['boss'])" index="/settings/users">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
        <div class="header-right">
          <span class="user-name">{{ auth.user?.real_name }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32">
              {{ auth.user?.real_name?.charAt(0) }}
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="change-password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- Change password dialog -->
  <el-dialog v-model="changePwdVisible" title="修改密码" width="420px" :close-on-click-modal="false" @closed="resetChangePwdForm">
    <el-form ref="changePwdFormRef" :model="changePwdForm" :rules="changePwdRules" label-width="90px">
      <el-form-item label="旧密码" prop="old_password">
        <el-input v-model="changePwdForm.old_password" type="password" show-password placeholder="当前密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="changePwdForm.new_password" type="password" show-password placeholder="至少6位" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm_password">
        <el-input v-model="changePwdForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="changePwdVisible = false">取消</el-button>
      <el-button type="primary" :loading="changePwdSubmitting" @click="submitChangePassword">确认修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, User, UserFilled, Fold, Expand, Document, Setting, Tools,
  Wallet, Tickets, CreditCard, Money, Notebook, Coin,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword } from '@/api/users'

const router = useRouter()
const auth = useAuthStore()
const isCollapse = ref(false)

function hasAccess(roles) {
  return roles.includes(auth.userRole)
}

// ---- change password ----
const changePwdVisible = ref(false)
const changePwdSubmitting = ref(false)
const changePwdFormRef = ref(null)
const changePwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const changePwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== changePwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

function resetChangePwdForm() {
  changePwdForm.old_password = ''
  changePwdForm.new_password = ''
  changePwdForm.confirm_password = ''
  changePwdFormRef.value?.clearValidate()
}

async function submitChangePassword() {
  await changePwdFormRef.value.validate()
  changePwdSubmitting.value = true
  try {
    await changePassword(changePwdForm.old_password, changePwdForm.new_password)
    ElMessage.success('密码修改成功，请重新登录')
    changePwdVisible.value = false
    auth.logout()
    router.push('/login')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '密码修改失败')
  } finally {
    changePwdSubmitting.value = false
  }
}

// ---- header dropdown ----
function handleCommand(command) {
  if (command === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (command === 'change-password') {
    changePwdVisible.value = true
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.layout-aside {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #3d4d5e;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
  background: #fff;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-name {
  font-size: 14px;
  color: #606266;
}
.layout-main {
  background: #f0f2f5;
}
</style>
