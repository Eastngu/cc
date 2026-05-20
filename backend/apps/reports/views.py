from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order
from apps.finance.models import Receivable, Payable, Payment, MonthlyStatement
from apps.costing.models import OrderCost


class DashboardView(APIView):
    """经营看板数据 - 本月收入/支出/利润/应收余额"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        year, month = today.year, today.month

        # 本月收入 = 本月已出货订单总额
        monthly_revenue = Order.objects.filter(
            shipped_at__year=year, shipped_at__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # 本月支出 = 本月付款总额
        monthly_expense = Payment.objects.filter(
            type='pay', payment_date__year=year, payment_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 本月利润 = 收入 - 成本(有成本记录的订单)
        monthly_cost = OrderCost.objects.filter(
            order__shipped_at__year=year, order__shipped_at__month=month
        ).aggregate(total=Sum('total_cost'))['total'] or 0
        monthly_profit = monthly_revenue - monthly_cost

        # 应收余额
        receivable_balance = Receivable.objects.filter(
            status__in=['open', 'partial']
        ).aggregate(total=Sum('balance'))['total'] or 0

        # 上月同期数据(环比)
        if month == 1:
            last_year, last_month = year - 1, 12
        else:
            last_year, last_month = year, month - 1

        last_revenue = Order.objects.filter(
            shipped_at__year=last_year, shipped_at__month=last_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        return Response({
            'monthly_revenue': monthly_revenue,
            'monthly_expense': monthly_expense,
            'monthly_profit': monthly_profit,
            'receivable_balance': receivable_balance,
            'last_month_revenue': last_revenue,
            'revenue_change_rate': round(
                ((monthly_revenue - last_revenue) / last_revenue * 100) if last_revenue else 0, 1
            ),
        })


class RevenueTrendView(APIView):
    """近6个月收入/利润趋势"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        months_data = []

        for i in range(5, -1, -1):
            # Go back i months
            d = today.replace(day=1) - timedelta(days=i * 30)
            y, m = d.year, d.month

            revenue = Order.objects.filter(
                shipped_at__year=y, shipped_at__month=m
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            cost = OrderCost.objects.filter(
                order__shipped_at__year=y, order__shipped_at__month=m
            ).aggregate(total=Sum('total_cost'))['total'] or 0

            months_data.append({
                'month': f'{y}-{m:02d}',
                'revenue': revenue,
                'cost': cost,
                'profit': revenue - cost,
            })

        return Response(months_data)


class CustomerAnalysisView(APIView):
    """客户分析 - 各客户应收、回款率、利润贡献"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.customers.models import Customer

        customers = Customer.objects.filter(is_active=True)
        result = []

        for customer in customers:
            total_receivable = Receivable.objects.filter(
                customer=customer
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            total_received = Receivable.objects.filter(
                customer=customer
            ).aggregate(total=Sum('received_amount'))['total'] or 0

            collection_rate = round(
                (total_received / total_receivable * 100) if total_receivable else 0, 1
            )

            outstanding = Receivable.objects.filter(
                customer=customer, status__in=['open', 'partial']
            ).aggregate(total=Sum('balance'))['total'] or 0

            total_profit = OrderCost.objects.filter(
                order__customer=customer
            ).aggregate(total=Sum('profit'))['total'] or 0

            order_count = Order.objects.filter(customer=customer).count()

            if order_count > 0 or total_receivable > 0:
                result.append({
                    'customer_id': customer.id,
                    'customer_name': customer.short_name or customer.name,
                    'total_receivable': total_receivable,
                    'total_received': total_received,
                    'collection_rate': collection_rate,
                    'outstanding_balance': outstanding,
                    'total_profit': total_profit,
                    'order_count': order_count,
                })

        # Sort by outstanding balance descending
        result.sort(key=lambda x: x['outstanding_balance'], reverse=True)
        return Response(result)


class CostAnalysisView(APIView):
    """成本分析 - 各镀种/月度成本占比"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.processes.models import PlatingProcess

        processes = PlatingProcess.objects.filter(is_active=True)
        by_process = []

        for process in processes:
            data = OrderCost.objects.filter(
                order__plating_process=process
            ).aggregate(
                total_revenue=Sum('order__total_amount'),
                total_cost=Sum('total_cost'),
                total_profit=Sum('profit'),
                count=Count('id'),
            )
            if data['count'] > 0:
                by_process.append({
                    'process_name': process.name,
                    'order_count': data['count'],
                    'total_revenue': data['total_revenue'] or 0,
                    'total_cost': data['total_cost'] or 0,
                    'total_profit': data['total_profit'] or 0,
                    'avg_profit_rate': round(
                        ((data['total_profit'] or 0) / (data['total_revenue'] or 1)) * 100, 1
                    ),
                })

        return Response({
            'by_process': by_process,
        })
