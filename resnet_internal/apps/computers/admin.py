from django.contrib import admin

from .models import Computer


class ComputerAdmin(admin.ModelAdmin):
    list_display = ('department', 'sub_department', 'computer_name', 'ip_address', 'mac_address', 'model', 'serial_number', 'property_id', 'location', 'date_purchased', 'dn', 'description')
    list_filter = ('dhcp',)

admin.site.register(Computer, ComputerAdmin)