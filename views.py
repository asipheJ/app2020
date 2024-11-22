# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Account, Transaction
import hashlib
import random

# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Utility function to generate account numbers
def generate_account_number():
    return random.randint(1000000000, 9999999999)

# Register new user (Create Account)
def create_account(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        id_number = request.POST.get('id_number')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not first_name or not last_name or not phone_number or not id_number or not username or not password:
            messages.error(request, "All fields must be filled!")
            return render(request, 'create_account.html')

        hashed_password = hash_password(password)
        account_number = generate_account_number()

        account = Account.objects.create(
            account_number=account_number,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            id_number=id_number,
            username=username,
            password=hashed_password,
        )
        messages.success(request, f"Account created successfully! Your account number is {account_number}")
        return redirect('login')

    return render(request, 'create_account.html')

# Login functionality
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please fill both the username and password fields")
            return render(request, 'login.html')

        hashed_password = hash_password(password)
        try:
            account = Account.objects.get(username=username, password=hashed_password)
            messages.success(request, "Login successful!")
            return redirect('dashboard', account_id=account.id)
        except Account.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

# Dashboard to handle account operations
def dashboard(request, account_id):
    account = Account.objects.get(id=account_id)
    
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = float(request.POST.get('amount'))

        if transaction_type == "deposit":
            account.balance += amount
            account.save()
            Transaction.objects.create(account=account, transaction_type="Deposit", amount=amount)
            messages.success(request, f"R{amount:.2f} deposited successfully.")
        elif transaction_type == "withdraw":
            if account.balance < amount:
                messages.error(request, "Insufficient funds")
            else:
                account.balance -= amount
                account.save()
                Transaction.objects.create(account=account, transaction_type="Withdraw", amount=amount)
                messages.success(request, f"R{amount:.2f} withdrawn successfully.")
        elif transaction_type == "transfer":
            transfer_account_number = request.POST.get('transfer_to_account')
            try:
                transfer_account = Account.objects.get(account_number=transfer_account_number)
                if account.balance < amount:
                    messages.error(request, "Insufficient funds")
                else:
                    account.balance -= amount
                    transfer_account.balance += amount
                    account.save()
                    transfer_account.save()
                    Transaction.objects.create(account=account, transaction_type="Transfer", amount=amount)
                    Transaction.objects.create(account=transfer_account, transaction_type="Transfer", amount=amount)
                    messages.success(request, f"R{amount:.2f} transferred successfully.")
            except Account.DoesNotExist:
                messages.error(request, "Invalid account number")

    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    return render(request, 'dashboard.html', {'account': account, 'transactions': transactions})

