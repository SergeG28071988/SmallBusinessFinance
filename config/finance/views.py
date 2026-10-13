
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from .models import Account, Category, Transaction


def dashboard(request):
    """Главная панель с основными финансовыми показателями."""

    active_accounts = Account.objects.filter(is_active=True)

    opening_balance = active_accounts.aggregate(
        total=Sum('opening_balance')
    )['total'] or 0

    totals = Transaction.objects.aggregate(
        income=Sum(
            'amount',
            filter=Q(category__category_type=Category.CategoryType.INCOME),
            default=0,
        ),
        expenses=Sum(
            'amount',
            filter=Q(category__category_type=Category.CategoryType.EXPENSE),
            default=0,
        ),
    )

    total_income = totals['income']
    total_expenses = totals['expenses']
    current_balance = opening_balance + total_income - total_expenses

    latest_transactions = (
        Transaction.objects
        .select_related('account', 'category')
        .order_by('-date', '-id')[:10]
    )

    context = {
        'active_accounts_count': active_accounts.count(),
        'active_categories_count': Category.objects.filter(
            is_active=True
        ).count(),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'latest_transactions': latest_transactions,
    }

    return render(request, 'finance/dashboard.html', context)


def transactions(request):
    """Список финансовых операций."""

    transaction_list = (
        Transaction.objects
        .select_related('account', 'category')
        .order_by('-date', '-id')
    )

    context = {
        'transactions': transaction_list,
        'accounts': Account.objects.filter(is_active=True),
        'categories': Category.objects.filter(is_active=True),
    }

    return render(request, 'finance/transactions.html', context)


def reports(request):
    """Финансовая отчётность и данные для графиков."""

    totals = Transaction.objects.aggregate(
        income=Sum(
            'amount',
            filter=Q(category__category_type=Category.CategoryType.INCOME),
            default=0,
        ),
        expenses=Sum(
            'amount',
            filter=Q(category__category_type=Category.CategoryType.EXPENSE),
            default=0,
        ),
    )

    monthly_report = list(
        Transaction.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum(
                'amount',
                filter=Q(category__category_type=Category.CategoryType.INCOME),
                default=0,
            ),
            expenses=Sum(
                'amount',
                filter=Q(category__category_type=Category.CategoryType.EXPENSE),
                default=0,
            ),
        )
        .order_by('month')
    )

    for item in monthly_report:
        item['net_result'] = item['income'] - item['expenses']

    income_by_category = list(
        Category.objects
        .filter(
            category_type=Category.CategoryType.INCOME,
            transactions__isnull=False,
        )
        .values('name')
        .annotate(total=Sum('transactions__amount'))
        .order_by('-total')
    )

    expenses_by_category = list(
        Category.objects
        .filter(
            category_type=Category.CategoryType.EXPENSE,
            transactions__isnull=False,
        )
        .values('name')
        .annotate(total=Sum('transactions__amount'))
        .order_by('-total')
    )

    total_income = totals['income']
    total_expenses = totals['expenses']

    chart_data = {
        'months': [
            item['month'].strftime('%m.%Y')
            for item in monthly_report
        ],
        'monthly_income': [
            float(item['income'])
            for item in monthly_report
        ],
        'monthly_expenses': [
            float(item['expenses'])
            for item in monthly_report
        ],
        'monthly_result': [
            float(item['net_result'])
            for item in monthly_report
        ],
        'expense_categories': [
            item['name']
            for item in expenses_by_category
        ],
        'expense_category_totals': [
            float(item['total'])
            for item in expenses_by_category
        ],
    }

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_result': total_income - total_expenses,
        'monthly_report': monthly_report,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'chart_data': chart_data,
    }

    return render(request, 'finance/reports.html', context)
