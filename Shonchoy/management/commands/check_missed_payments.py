from django.core.management.base import BaseCommand
from Shonchoy.models import Loan, Notification
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Check for missed loan payments and generate notifications.'

    def handle(self, *args, **kwargs):
        for loan in Loan.objects.all():
            if loan.due_amount() > 0:
                for i in range(loan.installments):
                    expected_due = loan.start_date + timedelta(days=30 * (i + 1))
                    if expected_due < date.today():
                        Notification.objects.get_or_create(
                            member=loan.member,
                            related_loan=loan,
                            notification_type='LOAN_DUE',
                            message=f"Missed payment: Installment {i+1} for ${loan.amount/loan.installments:.2f} was due on {expected_due.strftime('%b %d, %Y')}.",
                        )
        self.stdout.write(self.style.SUCCESS('Missed payment check complete.'))
