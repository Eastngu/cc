import calendar
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = '填充演示数据（幂等，可重复运行）'

    def handle(self, *args, **options):
        self.stdout.write('开始填充演示数据...')
        random.seed(42)

        users = self._create_users()
        customers = self._create_customers()
        processes = self._create_processes()
        self._create_pricing_rules(customers, processes)
        orders = self._create_orders(customers, processes, users)
        self._create_costs(orders)
        payables = self._create_payables()
        receivables = self._create_receivables(customers, orders)
        self._create_statements(customers, orders, users)
        self._create_payments(receivables, payables, users)

        self.stdout.write(self.style.SUCCESS('演示数据填充完成！'))

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def _create_users(self):
        from apps.users.models import User

        users = {}

        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('admin123')
            admin.real_name = '老板'
            admin.role = 'boss'
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.stdout.write('  创建用户: admin')
        else:
            self.stdout.write('  跳过用户: admin（已存在）')
        users['admin'] = admin

        caiwu, created = User.objects.get_or_create(username='caiwu')
        if created:
            caiwu.set_password('caiwu123')
            caiwu.real_name = '财务小王'
            caiwu.role = 'finance'
            caiwu.save()
            self.stdout.write('  创建用户: caiwu')
        else:
            self.stdout.write('  跳过用户: caiwu（已存在）')
        users['caiwu'] = caiwu

        chejian, created = User.objects.get_or_create(username='chejian')
        if created:
            chejian.set_password('chejian123')
            chejian.real_name = '车间张主管'
            chejian.role = 'workshop'
            chejian.save()
            self.stdout.write('  创建用户: chejian')
        else:
            self.stdout.write('  跳过用户: chejian（已存在）')
        users['chejian'] = chejian

        return users

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------
    def _create_customers(self):
        from apps.customers.models import Customer

        customer_data = [
            {
                'name': '深圳市鑫达电子有限公司',
                'short_name': '鑫达电子',
                'contact_person': '王经理',
                'phone': '13800001001',
                'payment_terms': 30,
                'default_billing_type': 'area',
            },
            {
                'name': '东莞市恒利五金制品厂',
                'short_name': '恒利五金',
                'contact_person': '李总',
                'phone': '13800001002',
                'payment_terms': 60,
                'default_billing_type': 'weight',
            },
            {
                'name': '广州市精密模具有限公司',
                'short_name': '精密模具',
                'contact_person': '张工',
                'phone': '13800001003',
                'payment_terms': 30,
                'default_billing_type': 'piece',
            },
            {
                'name': '佛山市永盛金属表面处理有限公司',
                'short_name': '永盛金属',
                'contact_person': '陈经理',
                'phone': '13800001004',
                'payment_terms': 45,
                'default_billing_type': 'area',
            },
            {
                'name': '惠州市科达电器有限公司',
                'short_name': '科达电器',
                'contact_person': '刘总',
                'phone': '13800001005',
                'payment_terms': 30,
                'default_billing_type': 'area',
            },
        ]

        customers = {}
        for data in customer_data:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            customers[data['short_name']] = customer
            if created:
                self.stdout.write(f"  创建客户: {data['short_name']}")
            else:
                self.stdout.write(f"  跳过客户: {data['short_name']}（已存在）")

        return customers

    # ------------------------------------------------------------------
    # PlatingProcesses
    # ------------------------------------------------------------------
    def _create_processes(self):
        from apps.processes.models import PlatingProcess

        process_data = [
            {'name': '镀锌', 'code': 'DU-ZN', 'unit': 'area',   'base_price': Decimal('0.35')},
            {'name': '镀镍', 'code': 'DU-NI', 'unit': 'area',   'base_price': Decimal('0.55')},
            {'name': '镀铬', 'code': 'DU-CR', 'unit': 'area',   'base_price': Decimal('0.80')},
            {'name': '镀铜', 'code': 'DU-CU', 'unit': 'weight', 'base_price': Decimal('12.00')},
            {'name': '镀锡', 'code': 'DU-SN', 'unit': 'piece',  'base_price': Decimal('0.25')},
        ]

        processes = {}
        for data in process_data:
            process, created = PlatingProcess.objects.get_or_create(
                code=data['code'],
                defaults=data,
            )
            processes[data['name']] = process
            if created:
                self.stdout.write(f"  创建工艺: {data['name']}")
            else:
                self.stdout.write(f"  跳过工艺: {data['name']}（已存在）")

        return processes

    # ------------------------------------------------------------------
    # PricingRules
    # ------------------------------------------------------------------
    def _create_pricing_rules(self, customers, processes):
        from apps.processes.models import PricingRule

        rules = [
            {
                'customer':        customers['鑫达电子'],
                'plating_process': processes['镀锌'],
                'unit_price':      Decimal('0.3200'),
                'min_charge':      Decimal('100.00'),
                'effective_date':  date(2025, 1, 1),
            },
            {
                'customer':        customers['鑫达电子'],
                'plating_process': processes['镀镍'],
                'unit_price':      Decimal('0.5000'),
                'min_charge':      Decimal('150.00'),
                'effective_date':  date(2025, 1, 1),
            },
            {
                'customer':        customers['恒利五金'],
                'plating_process': processes['镀铜'],
                'unit_price':      Decimal('11.5000'),
                'min_charge':      Decimal('500.00'),
                'effective_date':  date(2025, 1, 1),
            },
            {
                'customer':        customers['精密模具'],
                'plating_process': processes['镀铬'],
                'unit_price':      Decimal('0.7500'),
                'min_charge':      Decimal('200.00'),
                'effective_date':  date(2025, 1, 1),
            },
        ]

        for rule in rules:
            _, created = PricingRule.objects.get_or_create(
                customer=rule['customer'],
                plating_process=rule['plating_process'],
                effective_date=rule['effective_date'],
                defaults={
                    'unit_price': rule['unit_price'],
                    'min_charge': rule['min_charge'],
                },
            )
            if created:
                cname = rule['customer'].short_name
                pname = rule['plating_process'].name
                self.stdout.write(f'  创建定价规则: {cname} × {pname}')

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------
    def _create_orders(self, customers, processes, users):
        from apps.orders.models import Order

        # Idempotency: skip if DEMO orders already exist
        if Order.objects.filter(remark='DEMO').exists():
            self.stdout.write('  跳过订单创建（演示订单已存在）')
            return list(Order.objects.filter(remark='DEMO'))

        today = date.today()

        # ---- date helpers ------------------------------------------------
        def _safe_date(year, month, day):
            max_day = calendar.monthrange(year, month)[1]
            return date(year, month, min(day, max_day))

        def cur(day):
            return _safe_date(today.year, today.month, min(day, today.day))

        # last month
        lm_year  = today.year  if today.month > 1 else today.year - 1
        lm_month = today.month - 1 if today.month > 1 else 12

        def lm(day):
            return _safe_date(lm_year, lm_month, day)

        # month before last
        m2_year  = lm_year  if lm_month > 1 else lm_year - 1
        m2_month = lm_month - 1 if lm_month > 1 else 12

        def m2(day):
            return _safe_date(m2_year, m2_month, day)

        # ---- order definitions -------------------------------------------
        # fmt: (customer_key, process_name, product_name, spec,
        #        quantity, unit, unit_price, status,
        #        received_at, completed_at, shipped_at)
        TEMPLATES = [
            # ── Pending (5) ────────────────────────────────────────────────
            ('鑫达电子', '镀锌', '手机外壳',    'Al-A6061',           Decimal('1500'), 'dm²', Decimal('0.3200'), 'pending',    cur(8),  None,     None),
            ('永盛金属', '镀镍', '散热片',      'CU-T2-80x60mm',      Decimal('2000'), 'dm²', Decimal('0.5500'), 'pending',    cur(10), None,     None),
            ('科达电器', '镀锌', '电器外壳',    'AL-6063',            Decimal('3000'), 'dm²', Decimal('0.3500'), 'pending',    cur(12), None,     None),
            ('精密模具', '镀铬', '模具镶件',    'P20-50x50x30',       Decimal('800'),  'dm²', Decimal('0.7500'), 'pending',    cur(14), None,     None),
            ('恒利五金', '镀铜', '弹簧',        '65Mn-φ2.5x15',       Decimal('120'),  'kg',  Decimal('11.500'), 'pending',    cur(15), None,     None),

            # ── Processing (5) ─────────────────────────────────────────────
            ('鑫达电子', '镀镍', 'PCB连接器',   'JST-2.54mm',         Decimal('2500'), 'dm²', Decimal('0.5000'), 'processing', cur(3),  None,     None),
            ('永盛金属', '镀铬', '装饰面板',    'SS-304-200x150mm',   Decimal('1200'), 'dm²', Decimal('0.8000'), 'processing', cur(5),  None,     None),
            ('科达电器', '镀镍', '汽车门把手',  'ZN-AL合金',          Decimal('1800'), 'dm²', Decimal('0.5500'), 'processing', cur(6),  None,     None),
            ('恒利五金', '镀铜', '轴承套',      'GCr15-φ40x50',       Decimal('85'),   'kg',  Decimal('11.500'), 'processing', cur(7),  None,     None),
            ('精密模具', '镀锡', '连接端子',    'TYPE-A-5.08mm',      Decimal('5000'), '件',  Decimal('0.2500'), 'processing', cur(9),  None,     None),

            # ── Completed (5) ──────────────────────────────────────────────
            ('鑫达电子', '镀锌', '电子接插件',  'CU-H62-2P',          Decimal('4000'), 'dm²', Decimal('0.3200'), 'completed',  cur(1),  cur(min(5, today.day)),  None),
            ('永盛金属', '镀锌', 'LED支架',     'CU-T2-5050',         Decimal('6000'), 'dm²', Decimal('0.3500'), 'completed',  lm(20),  lm(28),   None),
            ('科达电器', '镀铬', '精密齿轮',    'M1-Z40-HRC58',       Decimal('900'),  'dm²', Decimal('0.8000'), 'completed',  lm(22),  lm(28),   None),
            ('恒利五金', '镀铜', '五金配件',    'ZN-5-混件',          Decimal('200'),  'kg',  Decimal('11.500'), 'completed',  lm(18),  lm(25),   None),
            ('精密模具', '镀铬', '模具镶件',    'S136-80x60x40',      Decimal('600'),  'dm²', Decimal('0.7500'), 'completed',  lm(15),  lm(22),   None),

            # ── Shipped – last month (5) ────────────────────────────────────
            ('鑫达电子', '镀锌', '手机外壳',    'Al-A6061-Type2',     Decimal('5000'), 'dm²', Decimal('0.3200'), 'shipped',    lm(2),   lm(10),   lm(12)),
            ('鑫达电子', '镀镍', '散热片',      'CU-T2-100x80mm',     Decimal('3000'), 'dm²', Decimal('0.5000'), 'shipped',    lm(5),   lm(15),   lm(17)),
            ('永盛金属', '镀铬', '装饰面板',    'SS-304-300x200mm',   Decimal('1500'), 'dm²', Decimal('0.8000'), 'shipped',    lm(3),   lm(12),   lm(14)),
            ('恒利五金', '镀铜', '螺丝螺母',    'M8x20-混',           Decimal('300'),  'kg',  Decimal('11.500'), 'shipped',    lm(1),   lm(8),    lm(10)),
            ('精密模具', '镀锡', 'PCB连接器',   'JST-2.0mm-2P',       Decimal('8000'), '件',  Decimal('0.2500'), 'shipped',    lm(6),   lm(14),   lm(16)),

            # ── Shipped – month before last (5) ────────────────────────────
            ('鑫达电子', '镀锌', '电器外壳',    'AL-6063-B型',        Decimal('4500'), 'dm²', Decimal('0.3200'), 'shipped',    m2(5),   m2(15),   m2(18)),
            ('永盛金属', '镀镍', '汽车门把手',  'ZN-AL-A型',          Decimal('2200'), 'dm²', Decimal('0.5500'), 'shipped',    m2(3),   m2(12),   m2(15)),
            ('科达电器', '镀锌', '散热片',      'AL-6061-60x40mm',    Decimal('5500'), 'dm²', Decimal('0.3500'), 'shipped',    m2(8),   m2(18),   m2(20)),
            ('恒利五金', '镀铜', '精密齿轮',    'M0.5-Z50-淬火',      Decimal('180'),  'kg',  Decimal('11.500'), 'shipped',    m2(2),   m2(10),   m2(12)),
            ('精密模具', '镀铬', '精密齿轮',    'M1-Z30-精密级',      Decimal('1000'), 'dm²', Decimal('0.7500'), 'shipped',    m2(10),  m2(20),   m2(22)),
        ]

        created_orders = []
        chejian = users['chejian']

        for (ckey, pname, prod, spec,
             qty, unit, price, status,
             recv, comp, ship) in TEMPLATES:

            order = Order(
                customer=customers[ckey],
                plating_process=processes[pname],
                product_name=prod,
                product_spec=spec,
                quantity=qty,
                unit=unit,
                unit_price=price,
                status=status,
                received_at=recv,
                completed_at=comp,
                shipped_at=ship,
                created_by=chejian,
                remark='DEMO',
            )
            order.save()
            created_orders.append(order)

        self.stdout.write(f'  创建订单: {len(created_orders)} 条')
        return created_orders

    # ------------------------------------------------------------------
    # OrderCosts
    # ------------------------------------------------------------------
    def _create_costs(self, orders):
        from apps.costing.models import OrderCost

        count = 0
        for order in orders:
            if order.status not in ('completed', 'shipped'):
                continue
            if OrderCost.objects.filter(order=order).exists():
                continue

            amount = float(order.total_amount)
            mat  = Decimal(str(round(amount * random.uniform(0.30, 0.50), 2)))
            elec = Decimal(str(round(amount * random.uniform(0.10, 0.20), 2)))
            lab  = Decimal(str(round(amount * random.uniform(0.15, 0.25), 2)))
            oth  = Decimal(str(round(amount * random.uniform(0.02, 0.05), 2)))

            OrderCost.objects.create(
                order=order,
                material_cost=mat,
                electricity_cost=elec,
                labor_cost=lab,
                other_cost=oth,
            )
            count += 1

        self.stdout.write(f'  创建成本记录: {count} 条')

    # ------------------------------------------------------------------
    # Payables
    # ------------------------------------------------------------------
    def _create_payables(self):
        from apps.finance.models import Payable

        today = date.today()
        payable_data = [
            {
                'supplier_name': '广州化工材料有限公司',
                'category':      'material',
                'total_amount':  Decimal('28500.00'),
                'due_date':      today + timedelta(days=15),
                'remark':        '5月份原材料采购款',
            },
            {
                'supplier_name': '南方电网',
                'category':      'electricity',
                'total_amount':  Decimal('15200.00'),
                'due_date':      today + timedelta(days=10),
                'remark':        '4月份电费账单',
            },
            {
                'supplier_name': '深圳环保设备公司',
                'category':      'equipment',
                'total_amount':  Decimal('45000.00'),
                'due_date':      today + timedelta(days=30),
                'remark':        '废水处理设备维修款',
            },
            {
                'supplier_name': '东莞物流有限公司',
                'category':      'other',
                'total_amount':  Decimal('3800.00'),
                'due_date':      today + timedelta(days=7),
                'remark':        '4-5月份运输费',
            },
            {
                'supplier_name': '佛山化学品供应商',
                'category':      'material',
                'total_amount':  Decimal('18600.00'),
                'due_date':      today + timedelta(days=20),
                'remark':        '镀液药品采购款',
            },
        ]

        payables = []
        for data in payable_data:
            existing = Payable.objects.filter(
                supplier_name=data['supplier_name'],
                total_amount=data['total_amount'],
            ).first()
            if existing:
                payables.append(existing)
                self.stdout.write(f"  跳过应付: {data['supplier_name']}（已存在）")
            else:
                p = Payable.objects.create(**data)
                payables.append(p)
                self.stdout.write(f"  创建应付: {data['supplier_name']}")

        return payables

    # ------------------------------------------------------------------
    # Receivables
    # ------------------------------------------------------------------
    def _create_receivables(self, customers, orders):
        from apps.finance.models import Receivable

        # Sum shipped order amounts by (customer_id, shipped year, shipped month)
        bucket = defaultdict(Decimal)
        for order in orders:
            if order.status == 'shipped' and order.shipped_at:
                key = (order.customer_id,
                       order.shipped_at.year,
                       order.shipped_at.month)
                bucket[key] += order.total_amount

        # customer_id -> Customer lookup
        cust_by_id = {c.id: c for c in customers.values()}

        receivables = []
        for (cid, year, month), total in bucket.items():
            customer = cust_by_id[cid]
            due_date = date(year, month, 1) + timedelta(days=customer.payment_terms + 30)

            rec, created = Receivable.objects.get_or_create(
                customer_id=cid,
                year=year,
                month=month,
                defaults={
                    'total_amount':    total,
                    'received_amount': Decimal('0'),
                    'due_date':        due_date,
                    'balance':         total,   # will be recomputed by save()
                },
            )
            receivables.append(rec)
            if created:
                self.stdout.write(
                    f'  创建应收: {customer.short_name} {year}-{month:02d} ¥{total:,.2f}'
                )
            else:
                self.stdout.write(
                    f'  跳过应收: {customer.short_name} {year}-{month:02d}（已存在）'
                )

        return receivables

    # ------------------------------------------------------------------
    # MonthlyStatements
    # ------------------------------------------------------------------
    def _create_statements(self, customers, orders, users):
        from apps.finance.models import MonthlyStatement

        today = date.today()

        lm_year  = today.year  if today.month > 1 else today.year - 1
        lm_month = today.month - 1 if today.month > 1 else 12

        m2_year  = lm_year  if lm_month > 1 else lm_year - 1
        m2_month = lm_month - 1 if lm_month > 1 else 12

        # Group shipped orders by (customer_id, year, month)
        groups = defaultdict(list)
        for order in orders:
            if order.status == 'shipped' and order.shipped_at:
                key = (order.customer_id,
                       order.shipped_at.year,
                       order.shipped_at.month)
                groups[key].append(order)

        cust_by_id = {c.id: c for c in customers.values()}
        finance_user = users['caiwu']
        count = 0

        for (cid, year, month), month_orders in groups.items():
            is_m2 = (year == m2_year and month == m2_month)
            is_lm = (year == lm_year and month == lm_month)
            if not (is_m2 or is_lm):
                continue

            status = 'confirmed' if is_m2 else 'draft'
            total  = sum(o.total_amount for o in month_orders)
            customer = cust_by_id[cid]

            try:
                stmt, created = MonthlyStatement.objects.get_or_create(
                    customer_id=cid,
                    year=year,
                    month=month,
                    defaults={
                        'total_amount': total,
                        'adjustment':   Decimal('0'),
                        'status':       status,
                        'confirmed_by': finance_user if status == 'confirmed' else None,
                        'confirmed_at': timezone.now() if status == 'confirmed' else None,
                    },
                )
                if created:
                    stmt.orders.set(month_orders)
                    count += 1
                    self.stdout.write(
                        f'  创建对账单: {customer.short_name} {year}-{month:02d} [{status}]'
                    )
                else:
                    self.stdout.write(
                        f'  跳过对账单: {customer.short_name} {year}-{month:02d}（已存在）'
                    )
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(
                        f'  跳过对账单: {customer.short_name} {year}-{month:02d}: {exc}'
                    )
                )

        self.stdout.write(f'  对账单合计: {count} 条')

    # ------------------------------------------------------------------
    # Payments
    # ------------------------------------------------------------------
    def _create_payments(self, receivables, payables, users):
        from apps.finance.models import Payment

        today = date.today()
        caiwu = users['caiwu']

        lm_year  = today.year  if today.month > 1 else today.year - 1
        lm_month = today.month - 1 if today.month > 1 else 12

        m2_year  = lm_year  if lm_month > 1 else lm_year - 1
        m2_month = lm_month - 1 if lm_month > 1 else 12

        count = 0

        # ---- Receive payments for shipped receivables --------------------
        for rec in receivables:
            if Payment.objects.filter(receivable=rec).exists():
                continue

            is_m2 = (rec.year == m2_year and rec.month == m2_month)
            is_lm = (rec.year == lm_year and rec.month == lm_month)

            if is_m2:
                # Fully settled – paid in the following month
                payment_date = date(lm_year, lm_month, 15)
                Payment.objects.create(
                    type='receive',
                    customer=rec.customer,
                    receivable=rec,
                    amount=rec.total_amount,
                    payment_method='transfer',
                    payment_date=payment_date,
                    created_by=caiwu,
                    remark='DEMO',
                )
                count += 1

            elif is_lm:
                # Partially paid (60-80 %)
                rate   = Decimal(str(round(random.uniform(0.60, 0.80), 2)))
                amount = (rec.total_amount * rate).quantize(Decimal('0.01'))
                payment_date = today - timedelta(days=random.randint(3, 15))
                Payment.objects.create(
                    type='receive',
                    customer=rec.customer,
                    receivable=rec,
                    amount=amount,
                    payment_method='transfer',
                    payment_date=payment_date,
                    created_by=caiwu,
                    remark='DEMO',
                )
                count += 1

        # ---- Pay payments for material / electricity payables ------------
        for payable in payables:
            if payable.category not in ('material', 'electricity'):
                continue
            if Payment.objects.filter(payable=payable).exists():
                continue

            rate   = Decimal(str(round(random.uniform(0.50, 0.70), 2)))
            amount = (payable.total_amount * rate).quantize(Decimal('0.01'))
            payment_date = today - timedelta(days=random.randint(5, 20))
            Payment.objects.create(
                type='pay',
                payable=payable,
                amount=amount,
                payment_method='transfer',
                payment_date=payment_date,
                created_by=caiwu,
                remark='DEMO',
            )
            count += 1

        self.stdout.write(f'  创建收付款记录: {count} 条')
