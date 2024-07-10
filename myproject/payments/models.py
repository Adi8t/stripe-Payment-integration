from django.db import models

# Create your models here.
class Product(models.Model):
    stri_product_id = models.CharField(max_length=100, null=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        db_table= "product table"
     

class Price(models.Model):
    product = models.ForeignKey(Product , on_delete = models.CASCADE)
    stri_price_id = models.CharField(max_length = 100, null = True, editable = False)
    unit_amount = models.IntegerField()
    currency = models.CharField(max_length = 10)
    interval = models.CharField(max_length=20, choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='month')
    interval_count = models.IntegerField(default=1)

    def __str__(self) :
        return f"{self.product.name} - {self.unit_amount} {self.currency}"
    
class Customer(models.Model):
    stri_customer_id = models.CharField(max_length=100, editable=False)
    name = models.CharField(max_length = 20)
    email = models.EmailField()

class Subscription(models.Model):
    stri_customer_id = models.CharField(max_length=100 , null=True , editable=False)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    price = models.ForeignKey(Price, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} - {self.price.unit_amount} {self.price.currency}"












    
