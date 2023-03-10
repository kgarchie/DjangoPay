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
    return render(request, 'index.html')


def make_payment(request):
    form = SendMoneyForm(user=request.user)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=False)
            # subtract money from the money_sender
            money_sender = User.objects.get(id=request.user.id)

            # check if the money_sender has enough balance
            if money_sender.balance < form.cleaned_data.get('amount'):
                context['error'] = 'Insufficient balance'
                return render(request, 'send_money.html', context)
            money_sender.balance -= form.cleaned_data.get('amount')
            money_sender.save()

            # add money to the money_receiver
            money_receiver = User.objects.get(id=form.cleaned_data['money_to'].id)
            money_receiver.balance += form.cleaned_data.get('amount')
            money_receiver.save()

            # save the transaction
            form.save()
        else:
            context['error'] = form.errors
            return render(request, 'send_money.html', context)
    return render(request, 'send_money.html', context)


@receiver(post_save, sender=Transaction)
def send_notification(notification_sender, instance, created, **kwargs):
    if created:
        # Send notification to the receiver
        notification_receiver = User.objects.get(id=instance.money_to.id)
        message = 'You have received ' + str(instance.amount) + ' from ' + instance.money_from.username

        # Save the notification
        notification = Notification(transaction=instance, receiver=notification_receiver, message=message)
        notification.save()

        # Send notification to the notification_sender
        notification_sender = User.objects.get(id=instance.money_from.id)
        message = 'You have sent ' + str(instance.amount) + ' to ' + instance.money_to.username

        # Save the notification
        notification = Notification(transaction=instance, receiver=notification_sender, message=message)
        notification.save()


@login_required(login_url='/login/')
def transaction_history(request):
    if request.user.is_staff:
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(money_from=request.user) | Transaction.objects.filter(
            money_to=request.user)

    paginator = Paginator(transactions, 10)
    try:
        transactions = paginator.get_page(request.GET.get('page'))
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request, 'dashboard.html', {'transactions': transactions})


def dashboard(request):
    return transaction_history(request)


def login(request):
    form = LoginForm()
    context = {'form': form}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                context['error'] = 'Invalid username or password'
                return render(request, 'login.html', context)
        else:
            context['error'] = form.errors
            return render(request, 'login.html', context)
    return render(request, 'login.html', context)


def logout(request):
    auth_logout(request)
    return redirect('login')


def register(request):
    form = RegisterForm()
    context = {'form': form}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            context['error'] = form.errors
            return render(request, 'register.html', context)
    return render(request, 'register.html', context)
