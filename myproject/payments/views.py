from django.shortcuts import render
import stripe
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Price, Customer, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
@api_view(["POST"])
def create_product(request):
    if request.method == "POST":
        name = request.data.get("name")
        description = request.data.get("description")
        if not name and not description:
            return Response({"name": "Name and description required.."})

    product = stripe.Product.create(name=name, description=description)
    Product.objects.create(
        stri_product_id=product.id, name=product.name, description=product.description
    )
    return Response(
        {
            "stri_product_id": product.id,
            "name": product.name,
            "description": product.description,
        }
    )


stripe.api_key = settings.STRIPE_SECRET_KEY

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from .models import Product, Price  # Adjust import as per your models location

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["POST"])
def create_price(request):
    if request.method == "POST":
        unit_amount = request.data.get("unit_amount")
        currency = request.data.get("currency")
        product_id = request.data.get("product_id")
        interval = request.data.get("interval", "month")
        interval_count = request.data.get("interval_count", 1)

        if not unit_amount or not currency or not product_id:
            return Response(
                {"error": "Unit amount, currency, and product ID are required"},
                status=400,
            )

        try:
            # Retrieve the Product instance
            product = Product.objects.get(id=product_id)

            # Create Stripe price with recurring settings
            price = stripe.Price.create(
                unit_amount=unit_amount,
                currency=currency,
                product=product.stri_product_id,
                recurring={
                    "interval": interval,
                    "interval_count": interval_count,
                },
            )

            # Save to local database
            Price.objects.create(
                stri_price_id=price.id,
                unit_amount=price.unit_amount,
                currency=price.currency,
                product=product,
                interval=interval,
                interval_count=interval_count,
            )

            return Response(
                {
                    "price_id": price.id,
                    "unit_amount": price.unit_amount,
                    "currency": price.currency,
                },
                status=201,
            )

        except Product.DoesNotExist:
            return Response({"error": "Product not found"})


@api_view(["POST"])
def Customer_create(request):
    if request.method == "POST":
        name = request.data.get("name")
        email = request.data.get("email")
        if not name and not email:
            return Response({"name": " name and email both required..."})
        try:
            customer = stripe.Customer.create(name=name, email=email)
            Customer.objects.create(
                stri_customer_id=customer.id, name=customer.name, email=customer.email
            )
            return Response(
                {
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "customer_email": customer.email,
                }
            )
        except Exception:
            return Response({"error": " customer not valid"})


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Subscription, Customer, Price, Product
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(["POST"])
def create_subscription(request):
    if request.method != "POST":
        return Response({"error": "Method not allowed"}, status=405)

    customer_id = request.data.get("customer_id")
    price_id = request.data.get("price_id")

    try:
        # Retrieve the customer and price objects
        customer = Customer.objects.get(id=customer_id)
        price = Price.objects.get(id=price_id)
        product = price.product

        # Create a Stripe Checkout session for subscription
        session = stripe.checkout.Session.create(
            customer=customer.stri_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price.stri_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=settings.YOUR_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.YOUR_DOMAIN + "/cancel",
        )

        # Store subscription details in the database
        Subscription.objects.create(
            customer=customer,
            price=price,
            product=product, 
            stri_customer_id=session.customer, 
        )

        # Return the URL for redirection
        return Response({
            "redirect_url": session.url
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist."}, status=404)
    except Price.DoesNotExist:
        return Response({"error": "Price does not exist."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['POST'])
def customer_details(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)  # id ko `customer_id` se compare kar rahe hain
        return Response({
            "customer_id": customer.stri_customer_id,
            "name": customer.name,
        })
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=404)


# stripe.api_key = settings.STRIPE_SECRET_KEY

# @api_view(['POST'])
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

#     try:
#         # Verify the event using Stripe's library
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError:
#         # Invalid payload
#         return Response({'error': 'Invalid payload'}, status=400)

#     # Handle the event
#     if event['type'] == 'invoice.payment_succeeded':
#         invoice = event['data']['object']
#         subscription_id = invoice.get('subscription')
#         invoice_id = invoice.get('id')
#         invoice_url = invoice.get('hosted_invoice_url')

#         try:
#             # Update the subscription with the invoice details
#             subscription = Subscription.objects.get(stri_subscription_id=subscription_id)
#             subscription.invoice_id = invoice_id
#             subscription.invoice_url = invoice_url
#             subscription.save()

#             # Also update the customer with the invoice details
#             customer = subscription.customer
#             customer.invoice_id = invoice_id
#             customer.invoice_url = invoice_url
#             customer.save()

#         except Subscription.DoesNotExist:
#             return Response({'error': 'Subscription not found'}, status=404)
#         except Customer.DoesNotExist:
#             return Response({'error': 'Customer not found'}, status=404)

#     return Response({'status': 'success'}, status=200)
