<template>
  <el-dialog
    :title="isEdit ? '编辑客户' : '新增客户'"
    :model-value="visible"
    width="600px"
    @close="$emit('update:visible', false)"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="公司名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入完整公司名称" />
      </el-form-item>
      <el-form-item label="简称" prop="short_name">
        <el-input v-model="form.short_name" placeholder="如: ABC电子" />
      </el-form-item>
      <el-form-item label="联系人" prop="contact_person">
        <el-input v-model="form.contact_person" />
      </el-form-item>
      <el-form-item label="电话" prop="phone">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.address" />
      </el-form-item>
      <el-form-item label="月结天数" prop="payment_terms">
        <el-select v-model="form.payment_terms" style="width: 100%">
          <el-option :value="30" label="30天" />
          <el-option :value="60" label="60天" />
          <el-option :value="90" label="90天" />
        </el-select>
      </el-form-item>
      <el-form-item label="计费方式" prop="default_billing_type">
        <el-select v-model="form.default_billing_type" style="width: 100%">
          <el-option value="area" label="按面积(dm²)" />
          <el-option value="weight" label="按重量(kg)" />
          <el-option value="piece" label="按件数" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCustomerStore } from '@/stores/customers'

const props = defineProps({
  visible: Boolean,
  customer: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const formRef = ref(null)
const submitting = ref(false)
const store = useCustomerStore()

const form = reactive({
  name: '',
  short_name: '',
  contact_person: '',
  phone: '',
  address: '',
  payment_terms: 30,
  default_billing_type: 'area',
  remark: '',
})

const rules = {
  name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  payment_terms: [{ required: true, message: '请选择月结天数', trigger: 'change' }],
  default_billing_type: [{ required: true, message: '请选择计费方式', trigger: 'change' }],
}

watch(() => props.customer, (val) => {
  if (val) {
    isEdit.value = true
    Object.assign(form, val)
  } else {
    isEdit.value = false
    Object.assign(form, {
      name: '', short_name: '', contact_person: '', phone: '',
      address: '', payment_terms: 30, default_billing_type: 'area', remark: '',
    })
  }
}, { immediate: true })

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await store.editCustomer(props.customer.id, form)
      ElMessage.success('更新成功')
    } else {
      await store.addCustomer(form)
      ElMessage.success('创建成功')
    }
    emit('update:visible', false)
    emit('saved')
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}
</script>
