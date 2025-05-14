from django.db import models
from django.contrib.auth.models import User


class Webpage(models.Model):
    # Your fields here
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
    
from django.db.models import Sum

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    nid_number = models.CharField(max_length=20)

    def __str__(self):
        return str(self.user.username)

    def current_balance(self):
        deposits = self.transaction_set.filter(transaction_type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'] or 0
        cashouts = self.transaction_set.filter(transaction_type='CASH_OUT').aggregate(Sum('amount'))['amount__sum'] or 0
        return deposits - cashouts



class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('CASH_OUT', 'Cash Out'),
    )

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        user = self.member.user if isinstance(self.member, MemberProfile) else None
        return f"{self.transaction_type} of {self.amount} by {user.username if user else 'Unknown'}"


class Loan(models.Model):
    LOAN_TYPES = (
        ('PERSONAL', 'Personal Loan'),
        ('HOME', 'Home Loan'),
        ('EDUCATIONAL', 'Educational Loan'),
        ('AGRICULTURE', 'Agriculture Loan'),
    )

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField()
    start_date = models.DateField(auto_now_add=True)
    installments = models.PositiveIntegerField(default=1)


    def amount_paid(self):
        return self.loanpayment_set.aggregate(total=Sum('amount_paid'))['total'] or 0

    def due_amount(self):
        return self.amount - self.amount_paid()

    def __str__(self) -> str:
        user = self.member.user if isinstance(self.member, MemberProfile) else None
        return f"{self.loan_type} Loan for {user.username if user else 'Unknown'}"



class LoanPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"Payment of {self.amount_paid} for Loan ID {self.loan.id}"
    
from django.db import models
from django.utils import timezone
from .models import MemberProfile, Loan  # Adjust import if needed

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('INSTALLMENT_DUE', 'Installment Due'),
        ('LOAN_DUE', 'Loan Due'),  # Includes both due and fully paid
        ('DEPOSIT', 'Deposit'),
        ('CASH_OUT', 'Cash Out'),
        ('MISSED_PAYMENT', 'Missed Payment'),
        ('FULLY_PAID', 'Fully Paid'),
    ]

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    related_loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type} for {self.member.user.username} at {self.timestamp}"


class Organization(models.Model):
    name = models.CharField(max_length=100)


