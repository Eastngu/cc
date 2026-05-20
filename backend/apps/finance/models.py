from django.db import models
from django.conf import settings


class MonthlyStatement(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('sent', '已发送'),
    ]

    statement_no = models.CharField('对账单号', max_length=20, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, verbose_name='客户')
    year = models.IntegerField('年份')
    month = models.IntegerField('月份')
    total_amount = models.DecimalField('合计金额', max_digits=12, decimal_places=2, default=0)
    adjustment = models.DecimalField('调整金额', max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField('最终金额', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='确认人', related_name='confirmed_statements',
    )
    confirmed_at = models.DateTimeField('确认时间', null=True, blank=True)
    orders = models.ManyToManyField('orders.Order', blank=True, verbose_name='关联订单')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'monthly_statements'
        verbose_name = '月度对账单'
        verbose_name_plural = verbose_name
        ordering = ['-year', '-month']
        unique_together = ['customer', 'year', 'month']

    def __str__(self):
        return f'{self.statement_no} - {self.customer}'

    def save(self, *args, **kwargs):
        if not self.statement_no:
            self.statement_no = (
                f"ST{int(self.year)}{int(self.month):02d}{int(self.customer_id):04d}"
            )
        self.final_amount = self.total_amount + self.adjustment
        super().save(*args, **kwargs)


class Receivable(models.Model):
    STATUS_CHOICES = [
        ('open', '未结'),
        ('partial', '部分回款'),
        ('settled', '已结清'),
    ]

    receivable_no = models.CharField('应收单号', max_length=20, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, verbose_name='客户')
    year = models.IntegerField('年份')
    month = models.IntegerField('月份')
    total_amount = models.DecimalField('应收总额', max_digits=12, decimal_places=2)
    received_amount = models.DecimalField('已收金额', max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='open')
    due_date = models.DateField('到期日')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'receivables'
        verbose_name = '应收账款'
        verbose_name_plural = verbose_name
        ordering = ['-year', '-month']
        unique_together = ['customer', 'year', 'month']

    def __str__(self):
        return f'{self.receivable_no} - {self.customer}'

    def save(self, *args, **kwargs):
        if not self.receivable_no:
            self.receivable_no = f"AR{self.year}{self.month:02d}{self.customer_id:04d}"
        self.balance = self.total_amount - self.received_amount
        if self.balance <= 0:
            self.status = 'settled'
            self.balance = 0
        elif self.received_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'open'
        super().save(*args, **kwargs)


class Payable(models.Model):
    STATUS_CHOICES = [
        ('open', '未付'),
        ('partial', '部分付款'),
        ('settled', '已结清'),
    ]
    CATEGORY_CHOICES = [
        ('material', '原料'),
        ('electricity', '电费'),
        ('equipment', '设备'),
        ('other', '其他'),
    ]

    payable_no = models.CharField('应付单号', max_length=20, unique=True)
    supplier_name = models.CharField('供应商', max_length=100)
    category = models.CharField('类别', max_length=20, choices=CATEGORY_CHOICES, default='material')
    total_amount = models.DecimalField('应付总额', max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField('已付金额', max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='open')
    due_date = models.DateField('到期日')
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payables'
        verbose_name = '应付账款'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payable_no} - {self.supplier_name}'

    def save(self, *args, **kwargs):
        if not self.payable_no:
            from django.utils import timezone
            today = timezone.now()
            prefix = f"AP{today.strftime('%Y%m')}"
            last = Payable.objects.filter(payable_no__startswith=prefix).order_by('-payable_no').first()
            num = int(last.payable_no[-3:]) + 1 if last else 1
            self.payable_no = f"{prefix}{num:03d}"
        self.balance = self.total_amount - self.paid_amount
        if self.balance <= 0:
            self.status = 'settled'
            self.balance = 0
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'open'
        super().save(*args, **kwargs)


class Payment(models.Model):
    TYPE_CHOICES = [
        ('receive', '收款'),
        ('pay', '付款'),
    ]
    METHOD_CHOICES = [
        ('transfer', '银行转账'),
        ('cash', '现金'),
        ('acceptance', '承兑汇票'),
    ]

    payment_no = models.CharField('流水号', max_length=20, unique=True)
    type = models.CharField('类型', max_length=10, choices=TYPE_CHOICES)
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT,
        null=True, blank=True, verbose_name='客户',
    )
    receivable = models.ForeignKey(
        Receivable, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name='关联应收',
    )
    payable = models.ForeignKey(
        Payable, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name='关联应付',
    )
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    payment_method = models.CharField('支付方式', max_length=20, choices=METHOD_CHOICES, default='transfer')
    payment_date = models.DateField('支付日期')
    remark = models.TextField('备注', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name='创建人', null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = '收付款记录'
        verbose_name_plural = verbose_name
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f'{self.payment_no} - {self.get_type_display()} {self.amount}'

    def save(self, *args, **kwargs):
        if not self.payment_no:
            from django.utils import timezone
            today = timezone.now()
            prefix = f"PY{today.strftime('%Y%m%d')}"
            last = Payment.objects.filter(payment_no__startswith=prefix).order_by('-payment_no').first()
            num = int(last.payment_no[-3:]) + 1 if last else 1
            self.payment_no = f"{prefix}{num:03d}"
        super().save(*args, **kwargs)
        # Update related receivable/payable
        if self.type == 'receive' and self.receivable:
            r = self.receivable
            r.received_amount = Payment.objects.filter(receivable=r).aggregate(
                total=models.Sum('amount'))['total'] or 0
            r.save()
        elif self.type == 'pay' and self.payable:
            p = self.payable
            p.paid_amount = Payment.objects.filter(payable=p).aggregate(
                total=models.Sum('amount'))['total'] or 0
            p.save()
