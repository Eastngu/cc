from django.db import models


class PlatingProcess(models.Model):
    UNIT_CHOICES = [
        ('area', '面积(dm²)'),
        ('weight', '重量(kg)'),
        ('piece', '件数'),
    ]

    name = models.CharField('工艺名称', max_length=50)
    code = models.CharField('编码', max_length=20, unique=True)
    unit = models.CharField('计费单位', max_length=10, choices=UNIT_CHOICES, default='area')
    base_price = models.DecimalField('基础单价', max_digits=10, decimal_places=2, default=0)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plating_processes'
        verbose_name = '镀种工艺'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return f'{self.name}({self.code})'


class PricingRule(models.Model):
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE,
        null=True, blank=True, verbose_name='客户',
        help_text='留空表示通用定价',
    )
    plating_process = models.ForeignKey(
        PlatingProcess, on_delete=models.CASCADE, verbose_name='镀种工艺',
    )
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=4)
    min_charge = models.DecimalField('最低收费', max_digits=10, decimal_places=2, default=0)
    effective_date = models.DateField('生效日期')
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pricing_rules'
        verbose_name = '计费规则'
        verbose_name_plural = verbose_name
        ordering = ['-effective_date']

    def __str__(self):
        customer_name = self.customer.short_name if self.customer else '通用'
        return f'{customer_name} - {self.plating_process.name}: {self.unit_price}'
