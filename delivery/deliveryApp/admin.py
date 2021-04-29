from django.contrib import admin
from .models import Delivery_In,  Client, Delivery_Out, Bill,Viewer


admin.site.register(Delivery_Out)
admin.site.register(Client)
admin.site.register(Delivery_In)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("Bill_Id","delivery_in", "delivery_out","client","Status","Extracted_For_DelOut","Date_In", "Date_Sent")
    list_filter = ("delivery_in", "delivery_out","client","Status")

@admin.register(Viewer)
class ViewerAdmin(admin.ModelAdmin):
	list_display = ("Username", "Password", "Company")

