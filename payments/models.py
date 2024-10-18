# payments/models.py
from django.db import models

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('INIT', 'شروع شده'),
        ('SUCCESS', 'موفق'),
        ('FAIL', 'ناموفق'),
    ]

    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INIT')
    authority = models.CharField(max_length=255, null=True, blank=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
