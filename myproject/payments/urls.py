from django.contrib import admin
from django.urls import path ,include
from . import views
urlpatterns = [
    path('create-product/', 
         views.create_product, 
         name='create_product'),

    path('create-price/',
         views.create_price,
         name='create-price'),

    path('create-customer/',
         views.Customer_create,
         name="create_customer"),

    path('create-subscription/',
         views.create_subscription,
         name="create-subscription"),

    path('customer-details/<int:customer_id>/',
          views.customer_details,
          name='customer-details'),

    # path('stripe-webhook/',
    #       views.stripe_webhook,
    #       name='stripe-webhook/'),

]
