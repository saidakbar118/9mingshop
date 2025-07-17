from django.db import models

class Banner_model(models.Model):
    image = models.ImageField(upload_to='images/')

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

# Mahsulot modeli
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')

    old_price = models.DecimalField(max_digits=10, decimal_places=2)  # eski narx
    price = models.DecimalField(max_digits=10, decimal_places=2)      # yangi narx (aksiya narxi)

    created_at = models.DateTimeField(auto_now_add=True)
    
    is_free = models.BooleanField(default=False)

    @property
    def discount_percent(self):
        if self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    @property
    def has_discount(self):
        return self.old_price > self.price
    
    
class Cart(models.Model):
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart: {self.session_key}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    
    

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('oldindan', "Oldindan to‘lov"),
        ('olgandan', "Olgandan so‘ng to‘lov"),
    )

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.full_name}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
