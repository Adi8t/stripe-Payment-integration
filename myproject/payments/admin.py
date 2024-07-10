from django.contrib import admin

# Register your models here.
from .models import Product , Price ,Customer,Subscription
@admin.register(Product)
class Productpanel(admin.ModelAdmin):
    list_display = ["id",'stri_product_id','name','description']

@admin.register(Price)
class Pricepanel(admin.ModelAdmin):
    list_display = ["id","stri_price_id",'product','unit_amount','currency']

@admin.register(Customer)
class customerpanel(admin.ModelAdmin):
    list_display = ['id','stri_customer_id','name','email']

@admin.register(Subscription)
class  subscriptionpanel(admin.ModelAdmin):
    list_display = ['id','stri_customer_id','customer','price',]