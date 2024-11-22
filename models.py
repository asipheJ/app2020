# models.py

from django.db import models

class Account(models.Model):
    account_number = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    id_number = models.CharField(max_length=15)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=256)  # Store hashed password
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  # Deposit, Withdraw, Transfer
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
