from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    """Категория дохода или расхода."""

    class CategoryType(models.TextChoices):
        INCOME = 'income', 'Доход'
        EXPENSE = 'expense', 'Расход'

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    category_type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        verbose_name='Тип категории'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.category_type})'


class Account(models.Model):
    """Денежный счёт предприятия."""

    class AccountType(models.TextChoices):
        BANK = 'bank', 'Расчётный счёт'
        CASH = 'cash', 'Касса'
        OTHER = 'other', 'Другой счёт'

    name = models.CharField(
        max_length=100,
        verbose_name='Название счёта'
    )
    account_type = models.CharField(
        max_length=10,
        choices=AccountType.choices,
        verbose_name='Тип счёта'
    )
    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)],
        verbose_name='Начальный остаток'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Счёт'
        verbose_name_plural = 'Счета'
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Финансовая операция предприятия."""

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Счёт'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Категория'
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма'
    )
    date = models.DateField(
        default=timezone.localdate,
        verbose_name='Дата операции'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания записи'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения записи'
    )

    class Meta:
        verbose_name = 'Финансовая операция'
        verbose_name_plural = 'Финансовые операции'
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.date} — {self.category.name}: {self.amount}'
