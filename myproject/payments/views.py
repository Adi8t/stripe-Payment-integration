from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from .models import Product, Price, Customer, Subscription
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(["POST"])
def create_product(request):
    name = request.data.get("name")
    description = request.data.get("description")
    
    if not name or not description:
        return Response({"error": "Name and description are required"}, status=400)
    
    try:
        product = stripe.Product.create(name=name, description=description)
        Product.objects.create(
            stri_product_id=product.id, name=product.name, description=product.description
        )
        return Response({
            "stri_product_id": product.id,
            "name": product.name,
            "description": product.description,
        }, status=201)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def create_price(request):
    unit_amount = request.data.get("unit_amount")
    currency = request.data.get("currency")
    product_id = request.data.get("product_id")
    interval = request.data.get("interval", "month")
    interval_count = request.data.get("interval_count", 1)
    
    if not unit_amount or not currency or not product_id:
        return Response({"error": "Unit amount, currency, and product ID are required"}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        price = stripe.Price.create(
            unit_amount=unit_amount,
            currency=currency,
            product=product.stri_product_id,
            recurring={"interval": interval, "interval_count": interval_count},
        )
        Price.objects.create(
            stri_price_id=price.id,
            unit_amount=price.unit_amount,
            currency=price.currency,
            product=product,
            interval=interval,
            interval_count=interval_count,
        )
        return Response({
            "price_id": price.id,
            "unit_amount": price.unit_amount,
            "currency": price.currency,
        }, status=201)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def create_customer(request):
    name = request.data.get("name")
    email = request.data.get("email")
    
    if not name or not email:
        return Response({"error": "Name and email are required"}, status=400)
    
    try:
        customer = stripe.Customer.create(name=name, email=email)
        Customer.objects.create(
            stri_customer_id=customer.id, name=customer.name, email=customer.email
        )
        return Response({
            "customer_id": customer.id,
            "customer_name": customer.name,
            "customer_email": customer.email,
        }, status=201)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def create_subscription(request):
    customer_id = request.data.get("customer_id")
    price_id = request.data.get("price_id")
    
    try:
        customer = Customer.objects.get(id=customer_id)
        price = Price.objects.get(id=price_id)
        product = price.product
        
        session = stripe.checkout.Session.create(
            customer=customer.stri_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price.stri_price_id, "quantity": 1}],
            mode="subscription",
            success_url=settings.YOUR_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.YOUR_DOMAIN + "/cancel",
        )
        Subscription.objects.create(
            customer=customer,
            price=price,
            product=product,
            stri_customer_id=session.customer,
        )
        return Response({"redirect_url": session.url}, status=201)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist."}, status=404)
    except Price.DoesNotExist:
        return Response({"error": "Price does not exist."}, status=404)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def customer_details(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        return Response({
            "customer_id": customer.stri_customer_id,
            "name": customer.name,
        }, status=200)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=404)



@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'status': 'invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        subscription_id = subscription['id']
        invoice_id = subscription['latest_invoice']
        customer_id = subscription['customer']
        price_id = subscription['items']['data'][0]['price']['id']  # Assuming only one price per subscription

        try:
            customer = Customer.objects.get(stri_customer_id=customer_id)
            price = Price.objects.get(stri_price_id=price_id)
            product = price.product

            # Use get_or_create with defaults to avoid creating duplicates
            Subscription.objects.get_or_create(
                stri_subscription_id=subscription_id,
                defaults={
                    'invoice_id': invoice_id,
                    'customer': customer,
                    'price': price,
                    'product': product,
                }
            )
            return JsonResponse({'status': 'success'}, status=200)
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'customer not found'}, status=404)
        except Price.DoesNotExist:
            return JsonResponse({'status': 'price not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'event type not handled'}, status=200)

import stripe
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer

stripe.api_key = settings.STRIPE_SECRET_KEY
@api_view(['GET'])
def get_default_card(request, customer_id):
    try:
        # Retrieve customer from the Django database using the database ID
        db_customer = Customer.objects.get(id=customer_id)
        
        # Fetch the Stripe Customer ID from the database customer
        stripe_customer_id = db_customer.stri_customer_id
        
        # Retrieve the customer from Stripe using the Stripe Customer ID
        customer = stripe.Customer.retrieve(stripe_customer_id)
        
        # Log the customer object to debug
        print(f"Retrieved customer: {customer}")
        
        # Retrieve the default payment method ID
        default_payment_method_id = customer.invoice_settings.default_payment_method
        
        if not default_payment_method_id:
            return Response({"error": "Default payment method not found"}, status=404)
        
        # Retrieve the payment method details
        payment_method = stripe.PaymentMethod.retrieve(default_payment_method_id)
        
        # Log the payment method object to debug
        print(f"Retrieved payment method: {payment_method}")
        
        # Extract card details from the payment method
        card = payment_method.card
        
        return Response({
            'default_card_id': payment_method.id,
            'last4': card.last4,
            'exp_month': card.exp_month,
            'exp_year': card.exp_year
        }, status=200)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=404)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)

