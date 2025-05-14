from django.contrib import admin
from .models import MemberProfile, Transaction, Loan, LoanPayment, Organization, Notification 

admin.site.register([MemberProfile, Transaction, Loan, LoanPayment, Organization, Notification])  