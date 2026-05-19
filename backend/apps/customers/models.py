from django.db import models


class Customer(models.Model):
    BILLING_TYPE_CHOICES = [
        ('area', '按面积(dm²)'),
        ('weight', '按重量(kg)'),
        ('piece', '按件数'),
    ]

    name = models.CharField('公司名称', max_length=100)
    short_name = models.CharField('简称', max_length=20, blank=True)
    contact_person = models.CharField('联系人', max_length=20, blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    address = models.CharField('地址', max_length=200, blank=True)
    payment_terms = models.IntegerField('月结天数', default=30, help_text='如30/60/90')
    default_billing_type = models.CharField(
        '默认计费方式',
        max_length=10,
        choices=BILLING_TYPE_CHOICES,
        default='area',
    )
    remark = models.TextField('备注', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'customers'
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.short_name or self.name
