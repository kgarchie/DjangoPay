from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Transaction, User, Notification
from .forms import SendMoneyForm, RegisterForm, LoginForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('pay_app:dashboard')
    return render(request, 'index.html')


@login_required(login_url='/login/')
def make_payment(request):
    form = SendMoneyForm(user=request.user)
    context = {'form': form}
    if request.method == 'POST':
        form = SendMoneyForm(request.POST, user=request.user)
        if form.is_valid():
            form.save(commit=False)
            form.instance.money_from = User.objects.get(id=request.user.id)

            # check if the money_sender has enough balance
            if form.instance.money_from.balance < 0:
                context['error'] = 'Insufficient Balance'
                return render(request, 'send_money.html', context)

            # subtract money from the money_sender
            form.instance.money_from.balance -= form.instance.amount
            form.instance.money_from.save()

            # add money to the money_receiver)
            money_receiver = form.instance.money_to
            money_receiver.balance += form.instance.amount
            money_receiver.save()

            # save the transaction
            form.save()

            # change transaction status to True after successful transaction
            transaction = Transaction.objects.get(id=form.instance.id)
            transaction.status = True
            transaction.save()
            return redirect('pay_app:dashboard')
        else:
            context['error'] = 'Transaction not Successful | Please try again'
            return render(request, 'send_money.html', context)
    return render(request, 'send_money.html', context)


@receiver(post_save, sender=Transaction)
def send_notification(instance, created, **kwargs):
    if created:
        # Send notification to the receiver
        notification_receiver = User.objects.get(id=instance.money_to.id)
        notification_sender = User.objects.get(id=instance.money_from.id)
        message = 'You have received ' + str(instance.amount) + ' from ' + instance.money_from.username

        # Save the notification
        notification = Notification(transaction=instance, receiver=notification_receiver, message=message,
                                    sender=notification_sender)
        notification.save()

        # Send notification to the notification_sender
        message = 'You have sent ' + str(instance.amount) + ' to ' + instance.money_to.username

        # Save the notification
        notification = Notification(transaction=instance, receiver=notification_sender, message=message,
                                    sender=notification_sender)
        notification.save()


@login_required(login_url='/login/')
def transaction_history(request):
    context = {
        'user': User.objects.get(id=request.user.id)
    }
    if request.user.is_staff:
        transactions = Transaction.objects.all().order_by('-transaction_date')
    else:
        transactions = Transaction.objects.filter(money_from=request.user) | Transaction.objects.filter(
            money_to=request.user).order_by('-transaction_date')

    paginator = Paginator(transactions, 10)
    try:
        transactions = paginator.get_page(request.GET.get('page'))
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    context['transactions'] = transactions

    return render(request, 'dashboard.html', context)


def dashboard(request):
    return transaction_history(request)


def login(request):
    form = LoginForm()
    context = {'form': form}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('/')
            else:
                context['error'] = 'Invalid username or password'
                return render(request, 'login.html', context)
        else:
            context['error'] = form.errors
            return render(request, 'login.html', context)
    return render(request, 'login.html', context)


def logout(request):
    auth_logout(request)
    return redirect('pay_app:login')


def register(request):
    form = RegisterForm()
    context = {'form': form}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            password = form.cleaned_data.get('password')
            form.instance.set_password(password)
            form.save()
            user = authenticate(username=form.cleaned_data.get('username'), password=password)
            auth_login(request, user)
            return redirect('/')
        else:
            context['error'] = form.errors
            return render(request, 'register.html', context)
    return render(request, 'register.html', context)


@login_required(login_url='/login/')
def notifications(request):
    user_notifications = Notification.objects.filter(receiver=request.user, read=False).order_by('-date')
    for notification in user_notifications:
        notification.read = True
        notification.save()
    return render(request, 'notifications.html', {'notifications': user_notifications})


def accept_payment(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.accepted = True
    transaction.save()
    return redirect('pay_app:dashboard')


def reject_payment(request, id):
    transaction = Transaction.objects.get(id=id)
    transaction.accepted = False
    transaction.save()
    return redirect('pay_app:dashboard')


def success(request):
    return render(request, 'transaction_successful.html')
