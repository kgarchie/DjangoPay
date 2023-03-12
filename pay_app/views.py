from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Transaction, User, Notification
from .forms import SendMoneyForm, RegisterForm, LoginForm, RequestPaymentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


# Create your views here.
def index(request):
    context = {}
    try:
        user = User.objects.get(id=request.user.id)
        context = {'user': user}
    except User.DoesNotExist:
        pass
    if request.user.is_staff:
        return redirect('/admin/')
    return render(request, 'index.html', context)


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
            if form.errors:
                context['error'] = form.errors
            else:
                context['error'] = 'Transaction not Successful | Please try again'
            return render(request, 'send_money.html', context)
    return render(request, 'send_money.html', context)


@login_required(login_url='/login/')
def request_payment(request):
    form = RequestPaymentForm(user=request.user)
    context = {'form': form}
    if request.method == 'POST':
        form = RequestPaymentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save(commit=False)
            form.instance.money_to = User.objects.get(id=request.user.id)
            form.save()
            return redirect('pay_app:dashboard')
        else:
            context['error'] = 'Request not Successful | Please try again'
            return render(request, 'request_payment.html', context)
    return render(request, 'request_payment.html', context)


@receiver(post_save, sender=Transaction)
def send_notification(instance, created, **kwargs):
    if created:
        if instance.status:
            Notification.objects.create(
                transaction=instance,
                receiver=instance.money_from,
                sender=instance.money_from,
                message=f'You sent {instance.amount} to {instance.money_to.username}'
            )
            Notification.objects.create(
                transaction=instance,
                receiver=instance.money_to,
                sender=instance.money_from,
                message=f'You received {instance.amount} from {instance.money_from.username}'
            )
        else:
            Notification.objects.create(
                transaction=instance,
                receiver=instance.money_from,
                sender=instance.money_to,
                message=f'You have received a request of {instance.amount} payment to {instance.money_to.username}'
            )
            Notification.objects.create(
                transaction=instance,
                sender=instance.money_to,
                receiver=instance.money_from,
                message=f'You have sent a request of {instance.amount} payment to {instance.money_from.username}'
            )


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
def notifications(request, notification_id=None):
    user_notifications = Notification.objects.filter(receiver=request.user, read=False).order_by('-date')
    if notification_id:
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()
    return render(request, 'notifications.html', {'notifications': user_notifications})


@login_required(login_url='/login/')
def accept_payment(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()

        transaction = Transaction.objects.get(id=notification.transaction.id)
        transaction.status = True

        # subtract the amount from the sender
        money_sender = User.objects.get(id=transaction.money_from.id)
        money_sender.balance -= transaction.amount
        money_sender.save()

        # add the amount to the receiver
        money_receiver = User.objects.get(id=transaction.money_to.id)
        money_receiver.balance += transaction.amount
        money_receiver.save()

        # send notification to the sender
        message = 'You have accepted request of ' + str(
            transaction.amount) + ' payment from ' + transaction.money_to.username
        notification = Notification(transaction=transaction, receiver=money_sender, message=message,
                                    sender=money_sender)
        notification.save()

        # send notification to the receiver
        message = 'You have received ' + str(transaction.amount) + ' from ' + transaction.money_from.username
        notification = Notification(transaction=transaction, receiver=money_receiver, message=message,
                                    sender=money_sender)
        notification.save()

        transaction.save()

    except Transaction.DoesNotExist:
        return HttpResponse('Transaction does not exist')

    except User.DoesNotExist:
        return HttpResponse('User does not exist')

    except Notification.DoesNotExist:
        return HttpResponse('Notification does not exist')

    return redirect('pay_app:dashboard')


@login_required(login_url='/login/')
def reject_payment(request, notification_id):
    transaction = Transaction.objects.get(id=Notification.objects.get(id=notification_id).transaction.id)
    transaction.status = False
    transaction.committed = False
    transaction.save()
    return redirect('pay_app:dashboard')


def success(request):
    return render(request, 'transaction_successful.html')
