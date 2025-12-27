from django.contrib import admin
from .models import IPO, ClientApp, MasterClient


admin.site.register(IPO)
admin.site.register(MasterClient) # <-- Aa Navu Che

@admin.register(ClientApp)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'ipo', 'allotment_status', 'profit_share_45', 'owner')
    list_filter = ('ipo', 'allotment_status', 'owner')
    search_fields = ('nickname', 'pan_number')