from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待加工'),
        ('processing', '加工中'),
        ('completed', '已完工'),
        ('shipped', '已出货'),
    ]

    order_no = models.CharField('订单号', max_length=20, unique=True)
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT, verbose_name='客户',
    )
    plating_process = models.ForeignKey(
        'processes.PlatingProcess', on_delete=models.PROTECT, verbose_name='镀种工艺',
    )
    product_name = models.CharField('产品名称', max_length=100)
    product_spec = models.CharField('规格型号', max_length=100, blank=True)
    quantity = models.DecimalField('数量', max_digits=12, decimal_places=2)
    unit = models.CharField('单位', max_length=10)  # dm², kg, 件
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=4)
    total_amount = models.DecimalField('订单金额', max_digits=12, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    received_at = models.DateField('来料日期', null=True, blank=True)
    completed_at = models.DateField('完工日期', null=True, blank=True)
    shipped_at = models.DateField('出货日期', null=True, blank=True)
    remark = models.TextField('备注', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name='创建人', null=True, blank=True,
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.customer}'

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self._generate_order_no()
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_no():
        """Generate order number like DD202605001"""
        from django.utils import timezone
        today = timezone.now()
        prefix = f"DD{today.strftime('%Y%m')}"
        last_order = Order.objects.filter(
            order_no__startswith=prefix
        ).order_by('-order_no').first()
        if last_order:
            last_num = int(last_order.order_no[-3:])
            return f"{prefix}{last_num + 1:03d}"
        return f"{prefix}001"
