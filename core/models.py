from django.db import models
from django.contrib.auth.models import User

# 1. IPO Table
class IPO(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

# 2. NEW: Master Client (Kayami List)
class MasterClient(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)
    broker = models.CharField(max_length=50)
    demat_acc = models.CharField(max_length=50, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)

    def __str__(self): return self.nickname

# 3. Client App (Application for specific IPO)
class ClientApp(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE)
    
    # Data will be copied from MasterClient
    nickname = models.CharField(max_length=100)
    broker = models.CharField(max_length=50)
    demat_acc = models.CharField(max_length=50, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    
    is_applied = models.BooleanField(default=False, verbose_name="Applied?")
    ALLOTMENT_CHOICES = [('Pending', 'Pending'), ('Allotted', 'Allotted ✅'), ('Not Allotted', 'Not Allotted ❌')]
    allotment_status = models.CharField(max_length=20, choices=ALLOTMENT_CHOICES, default='Pending')

    upi_request_sent = models.BooleanField(default=False)
    payment_cleared = models.BooleanField(default=False)
    
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit_share_45 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    
    seller_name = models.CharField(max_length=50, blank=True)
    selling_method = models.CharField(max_length=50, blank=True)
    payout_done = models.BooleanField(default=False)
    
    device_login = models.CharField(max_length=50, blank=True)
    pending_task = models.TextField(blank=True)
    screenshot_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.profit_share_45 = float(self.total_profit) * 0.45
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.nickname} - {self.ipo.name}"