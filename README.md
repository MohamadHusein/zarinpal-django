# راهنمای پیاده سازی درگاه پرداخت زرین پال با جنگو

این پروژه نحوه‌ی پیاده‌سازی درگاه پرداخت **زرین پال** در جنگو را با استفاده از کتابخانه‌ی `az-iranian-bank-gateways` نشان می‌دهد.

## پیش‌نیازها

- Python 3.x
- جنگو
- استفاده از محیط مجازی (توصیه می‌شود)
- وابستگی‌های لازم را نصب کنید:
-  ```pip install django az-iranian-bank-gateways```

- 
تنظیمات settings.py
در فایل settings.py، اپلیکیشن‌ها و تنظیمات زرین پال را اضافه کنید:
```
  INSTALLED_APPS = [

    'payments.apps.PaymentsConfig',
    "azbankgateways",
]

AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "ZARINPAL": {
            "MERCHANT_CODE": "<YOUR MERCHANT CODE>",
        },
    },
    "IS_SAMPLE_FORM_ENABLE": True,
    "DEFAULT": "ZARINPAL",
    "CURRENCY": "IRR",
}
```





تنظیمات urls.py
در فایل urls.py، آدرس‌های مربوط به درگاه پرداخت را اضافه کنید:`from django.contrib import admin
```
from django.urls import path
from azbankgateways.urls import az_bank_gateways_urls
from payments.views import go_to_gateway_view, callback_gateway_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("bankgateways/", az_bank_gateways_urls()),
    path("go-to-gateway/", go_to_gateway_view),
    path("call-back-gateway/", callback_gateway_view),
]
```






ساخت مدل تراکنش
در فایل models.py، یک مدل برای ذخیره‌ی اطلاعات تراکنش‌ها تعریف کنید:
```
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

```





اجرای مایگریشن‌ها
برای ایجاد جداول مربوطه، دستورات مایگریشن را اجرا کنید:
```
python manage.py makemigrations
python manage.py migrate
```

## نکته مهم

اگر از **reverse proxy** و **HTTPS** استفاده می‌کنید، برای رفع موارد احتمالی حتماً تنظیمات زیر را انجام دهید: [تنظیمات Reverse Proxy](https://stackoverflow.com/questions/62047354/build-absolute-uri-with-https-behind-reverse-proxy/65934202#65934202)

--------






تنظیم ویوها برای شروع پرداخت و بازگشت از درگاه
در فایل views.py، کد مربوط به پرداخت و مدیریت بازگشت از درگاه را پیاده‌سازی کنید:
```
import logging
from django.http import HttpResponse, Http404
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException

def go_to_gateway_view(request):
    amount = 11000  # حداقل مبلغ 11000 تومان
    user_mobile_number = "09123456789"  # اختیاری/حتما باید با 0 شروع شود

    factory = bankfactories.BankFactory()
    try:
        bank = factory.auto_create(bank_models.BankType.ZARINPAL)
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(reverse("callback-gateway"))
        bank.set_mobile_number(user_mobile_number)  # اختیاری
        bank_record = bank.ready()

        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        raise e

def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    if bank_record.is_success:
        return HttpResponse("پرداخت با موفقیت انجام شد.")
    
    return HttpResponse("پرداخت ناموفق بود.")

```
















