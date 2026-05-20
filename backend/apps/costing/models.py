from django.db import models


class OrderCost(models.Model):
    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE,
        verbose_name='订单', related_name='cost',
    )
    material_cost = models.DecimalField('材料费', max_digits=10, decimal_places=2, default=0)
    electricity_cost = models.DecimalField('电费', max_digits=10, decimal_places=2, default=0)
    labor_cost = models.DecimalField('人工费', max_digits=10, decimal_places=2, default=0)
    other_cost = models.DecimalField('其他费用', max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField('总成本', max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField('利润', max_digits=10, decimal_places=2, default=0)
    profit_rate = models.DecimalField('利润率(%)', max_digits=5, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_costs'
        verbose_name = '订单成本'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_no} 成本'

    def save(self, *args, **kwargs):
        self.total_cost = (
            self.material_cost + self.electricity_cost +
            self.labor_cost + self.other_cost
        )
        order_amount = self.order.total_amount or 0
        self.profit = order_amount - self.total_cost
        if order_amount > 0:
            self.profit_rate = (self.profit / order_amount) * 100
        else:
            self.profit_rate = 0
        super().save(*args, **kwargs)
