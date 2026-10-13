from django.contrib import admin
from .models import Account, Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'is_active')
    list_filter = ('category_type', 'is_active')
    search_fields = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'account_type',
        'opening_balance',
        'is_active',
    )
    list_filter = ('account_type', 'is_active')
    search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'category',
        'account',
        'amount',
    )
    list_filter = (
        'date',
        'category__category_type',
        'category',
        'account',
    )
    search_fields = (
        'description',
        'category__name',
        'account__name',
    )
    date_hierarchy = 'date'

