# Generated by Django 5.2 on 2025-05-05 14:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Shonchoy', '0005_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('INSTALLMENT_DUE', 'Installment Due'), ('LOAN_DUE', 'Loan Due'), ('DEPOSIT', 'Deposit'), ('CASH_OUT', 'Cash Out'), ('MISSED_PAYMENT', 'Missed Payment'), ('FULLY_PAID', 'Fully Paid')], max_length=20),
        ),
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
