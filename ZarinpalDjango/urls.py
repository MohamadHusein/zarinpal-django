
from django.contrib import admin
from django.urls import path
from azbankgateways.urls import az_bank_gateways_urls
from payments.views import go_to_gateway_view , callback_gateway_view

urlpatterns = [
    path('admin/', admin.site.urls),
path("bankgateways/", az_bank_gateways_urls()),
path("go-to-gateway/", go_to_gateway_view),
path("call-back-gateway/", callback_gateway_view),
]
