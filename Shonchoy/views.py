from django.shortcuts import render, redirect
from .models import Loan, LoanPayment, MemberProfile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.utils import timezone
from .models import Loan, LoanPayment, Notification, MemberProfile
from .models import *

def webpage(request):
    try:
        webpage = Webpage.objects.all()
    except AttributeError:
        webpage = []
    context = {
        'webpage': webpage,
    }
    return render(request, template_name='pages/webpage.html', context=context)

def homepage(request):
    return render (request,template_name='pages\homepage.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        nid = request.POST.get('nid')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                # Create a new user
                user = User.objects.create_user(username=name, password=password, first_name=name) # Changed username to name
                # Create a MemberProfile
                MemberProfile.objects.create(user=user, phone_number=phone, nid_number=nid)
                login(request, user)  # Log the user in
                return redirect('signupsuccessful')  # Redirect to the success page
            except Exception as e:
                error_message = f"Signup failed: {e}"
                return render(request, 'pages/signup.html', {'error': error_message})
        else:
            error_message = "Passwords do not match."
            return render(request, 'pages/signup.html', {'error': error_message})
    else:
        return render(request, 'pages/signup.html')
    

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
                return render(request, 'pages/login.html', {'form': form})  # Re-render with errors
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'pages/login.html', {'form': form})  # Re-render with errors
    else:
        form = AuthenticationForm(request)
    return render(request, 'pages/login.html', {'form': form})

def signupsuccessful(request):
    return render(request, 'pages/signupsuccessful.html')

def home(request):
    return render (request,template_name='pages\home.html')
def mybank(request):
    return render (request,template_name='pages\mybank.html')

from datetime import date, timedelta


def loaninquiries(request):
    try:
        member = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist:
        messages.error(request, "Member profile not found.")
        return redirect('home')

    if request.method == 'POST':
        loan_type = request.POST.get('loan_type')
        amount = request.POST.get('amount')
        duration = request.POST.get('duration')
        installments = int(request.POST.get('installments', 1))

        if loan_type and amount and duration:
            try:
                loan = Loan.objects.create(
                    member=member,
                    loan_type=loan_type,
                    amount=amount,
                    duration_months=duration,
                    installments=installments
                )

                # Generate notifications for each installment due date
                per_installment = float(loan.amount) / installments
                for i in range(installments):
                    due_date = date.today() + timedelta(days=30 * (i + 1))
                    message = (
                        f"Installment {i + 1} of ${per_installment:.2f} is due on {due_date.strftime('%b %d, %Y')}."
                        if installments > 1 else
                        f"Full loan payment of ${loan.amount} is due on {due_date.strftime('%b %d, %Y')}."
                    )
                    Notification.objects.create(
                        member=member,
                        notification_type='INSTALLMENT_DUE' if installments > 1 else 'LOAN_DUE',
                        message=message,
                        related_loan=loan
                    )

                messages.success(request, 'Successfully applied for the loan!')
                return redirect('loaninquiries')
            except Exception as e:
                messages.error(request, f'Error applying for loan: {e}')
        else:
            messages.error(request, 'Please fill in all required fields.')

    loans = Loan.objects.filter(member=member).order_by('-start_date')
    return render(request, 'pages/loaninquiries.html', {'loans': loans})


@login_required
def notifications(request):
    member_profile = MemberProfile.objects.get(user=request.user)

    upcoming_deadlines = Notification.objects.filter(
        member=member_profile,
        notification_type='INSTALLMENT_DUE'
    ).order_by('timestamp')

    transaction_history = Notification.objects.filter(
        member=member_profile,
        notification_type__in=['DEPOSIT', 'CASH_OUT']
    ).order_by('-timestamp')

    loan_alerts = Notification.objects.filter(
        member=member_profile,
        notification_type__in=['LOAN_DUE', 'MISSED_PAYMENT', 'FULLY_PAID']
    ).order_by('-timestamp')

    return render(request, 'pages/notifications.html', {
        'upcoming_deadlines': upcoming_deadlines,
        'transaction_history': transaction_history,
        'loan_alerts': loan_alerts,
    })


def chartlist(request):
    return render (request,template_name='pages\chartlist.html')
from django.contrib.auth.decorators import login_required

@login_required
def currentstatus(request):
    try:
        member = MemberProfile.objects.get(user=request.user)
        transactions = Transaction.objects.filter(member=member).order_by('-date')
        loans = Loan.objects.filter(member=member).order_by('-start_date')

        # Calculate current balance
        balance = 0
        for t in transactions:
            if t.transaction_type == 'DEPOSIT':
                balance += t.amount
            elif t.transaction_type == 'CASH_OUT':
                balance -= t.amount

        loan_data = []
        for loan in loans:
            paid = LoanPayment.objects.filter(loan=loan).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
            due = loan.amount - paid
            loan_data.append({
                'loan': loan,
                'paid_amount': paid,
                'due_amount': due,
            })

        context = {
            'balance': balance,
            'transactions': transactions,
            'loan_data': loan_data,  
        }
        return render(request, 'pages/currentstatus.html', context)
    except MemberProfile.DoesNotExist:
        messages.error(request, "Member profile not found.")
        return redirect('home')


@login_required
def transaction(request):
    member_profile = MemberProfile.objects.get(user=request.user)

    
    transaction_history = Notification.objects.filter(
        member=member_profile,
        notification_type__in=['DEPOSIT', 'CASH_OUT']
    ).order_by('-timestamp')

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = float(request.POST.get('amount'))

        if transaction_type in ['DEPOSIT', 'CASH_OUT']:
            Transaction.objects.create(
                member=member_profile,
                transaction_type=transaction_type,
                amount=amount
            )
            Notification.objects.create(
                member=member_profile,
                notification_type=transaction_type,
                message=f"{transaction_type.replace('_', ' ').title()} of ${amount:.2f}"
            )
            messages.success(request, f"{transaction_type.replace('_', ' ').title()} of ${amount:.2f} completed successfully.")
            return redirect('transaction')

    return render(request, 'pages/transaction.html', {
        'transaction_history': transaction_history
    })
 

@login_required
def myloans(request):
    member_profile = get_object_or_404(MemberProfile, user=request.user)

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        amount = request.POST.get('amount')
        try:
            loan = Loan.objects.get(id=loan_id, member=member_profile)
            amount = float(amount)
            if amount > 0:
                LoanPayment.objects.create(
                    loan=loan,
                    amount_paid=amount,
                    payment_date=timezone.now()
                )

                
                Notification.objects.create(
                    member=member_profile,
                    notification_type='LOAN_DUE',
                    message=f"Paid ${amount:.2f} towards your loan.",
                    related_loan=loan
                )

                
                messages.success(request, f'Payment of ${amount:.2f} made successfully.')
                return redirect('myloans')
        except Exception as e:
            messages.error(request, f'Payment failed: {e}')
            return redirect('myloans')

    loans = Loan.objects.filter(member=member_profile).order_by('-start_date')
    loan_statuses = []

    for loan in loans:
        payments = LoanPayment.objects.filter(loan=loan)
        total_paid = sum(payment.amount_paid for payment in payments)
        remaining_balance = loan.amount - total_paid
        loan_statuses.append((loan, payments, total_paid, remaining_balance))

        
        if remaining_balance <= 0 and not Notification.objects.filter(related_loan=loan, notification_type='FULLY_PAID').exists():
            Notification.objects.create(
                member=member_profile,
                related_loan=loan,
                notification_type='FULLY_PAID',
                message=f'Loan fully paid off on {timezone.now().date()}.'
            )

    return render(request, 'pages/myloans.html', {'loan_statuses': loan_statuses})







def logout(request):
    return render(request, template_name='pages\logout.html')
