from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib import messages


from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def index_view(request):
    query = request.GET.get('search')
    category_slug = request.GET.get('category')

    # Barcha free bo'lmagan mahsulotlar
    products = Product.objects.filter(is_free=False)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if query:
        products = products.filter(title__icontains=query)

    context = {
        'products': products,  # filtrlangan mahsulotlar
        'categories': Category.objects.all(),
        'banner':Banner_model.objects.all(),
        'search_query': query,
    }
    return render(request, 'index.html', context)


def cart_view(request):
    return render(request, "cart.html")

def product_detail(request):
    return render(request,'product-details.html')


def get_cart(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('/cart/')

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('/cart/')

def update_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)
    if action == 'plus':
        item.quantity += 1
    elif action == 'minus':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            return redirect('/cart/')
    item.save()
    return redirect('/cart/')


def cart_view(request):
    cart = get_cart(request)

    if request.method == 'POST':
        # Foydalanuvchi ma'lumotlari
        full_name = request.POST.get('full_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        payment_type = request.POST.get('payment_type', 'olgandan')

        # Savat bo‘sh bo‘lsa
        if not cart.items.exists():
            return render(request, 'cart.html', {
                'cart': cart,
                'message': "❌ Savatcha bo‘sh!"
            })

        # Buyurtma yaratamiz
        order = Order.objects.create(
            full_name=full_name + " " + last_name,
            phone=phone,
            address=address,
            payment_type=payment_type,
            total_price=cart.total_price()
        )

        # Savatdagi mahsulotlarni qo‘shamiz
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Savatni tozalaymiz
        cart.items.all().delete()

        # Sessionda free uchun joy yaratamiz
        request.session['current_order_id'] = order.id
        request.session['selected_free'] = []

        # 50 mingdan katta bo‘lsa — free sahifaga
        if order.total_price >= 50000:
            return redirect(f'/free-products/{order.id}/')

        # Aks holda
        return render(request, 'cart.html', {
            'cart': cart,
            'message': "✅ Buyurtma qabul qilindi!"
        })

    return render(request, 'cart.html', {'cart': cart})



def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Keyinchalik to‘lov tizimi (Payme, Click) qo‘shamiz
    return render(request, 'payment.html', {'order': order})

def free_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Nechta mahsulot tanlash mumkinligini hisoblaymiz
    total = order.total_price
    if total >= 100000:
        max_count = 5
    elif total >= 75000:
        max_count = 4
    elif total >= 50000:
        max_count = 3
    else:
        return redirect('/')

    free_products = Product.objects.filter(is_free=True)
    selected_ids = request.session.get('selected_free', [])

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id not in selected_ids and len(selected_ids) < max_count:
            selected_ids.append(product_id)
            request.session['selected_free'] = selected_ids

        # Agar barcha tanlangan bo‘lsa — yakunlash
        if len(selected_ids) >= max_count:
            for pid in selected_ids:
                try:
                    product = Product.objects.get(id=pid, is_free=True)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=1,
                        price=0
                    )
                except:
                    continue
            request.session['selected_free'] = []
            return redirect('/thanks/')  # yoki boshqa sahifaga

    return render(request, 'free.html', {
        'free_products': free_products,
        'order': order,
        'max_count': max_count,
        'selected_count': len(selected_ids),
        'selected_ids': selected_ids,
    })
    
    
import requests
from django.http import JsonResponse

def reverse_geocode(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({'error': 'Koordinatalar topilmadi'}, status=400)

    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={
                'format': 'json',
                'lat': lat,
                'lon': lon,
                'zoom': 18,
                'addressdetails': 1
            },
            headers={
                'User-Agent': '9000-shop'
            }
        )
        data = response.json()
        manzil = data.get('display_name', 'Manzil topilmadi')
        return JsonResponse({'address': manzil})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




def free_info_view(request):
    free_products = Product.objects.filter(is_free=True).order_by('-created_at')
    return render(request, 'free-info.html', {
        'free_products': free_products,
        'selected_count': 0,  # Agar tanlash logikasi ishlatilsa
        'max_count': 99,      # Limit qo‘yish mumkin
        'selected_ids': []    # Tanlangan product id-lar listi
    })

def thanks_view(request):
    return render(request, 'thanks.html')

def media_view(request):
    return render(request, "sidebar/media.html")

def about_view(request):
    return render(request, 'sidebar/about.html')

def contact_view(request):
    return render(request, 'sidebar/contact.html')





#admin 
from django.views.decorators.csrf import csrf_exempt

def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/orders_list.html', {'orders': orders})

@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(pk=order_id)
            status = request.POST.get('status')
            order.status = status
            order.save()  # 🔥 MUHIM! — agar bu bo‘lmasa, o‘zgarish saqlanmaydi
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Buyurtma topilmadi'})
    return JsonResponse({'success': False, 'error': 'Noto‘g‘ri so‘rov'})
        


@csrf_exempt
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            Order.objects.get(id=order_id).delete()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Buyurtma topilmadi'})
    return JsonResponse({'success': False, 'error': 'Noto‘g‘ri so‘rov'})


def manage_categories(request):
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and 'add_category' in request.POST:
        if form.is_valid():
            form.save()
            return redirect('/manage/categories/')

    if request.method == 'POST' and 'edit_category' in request.POST:
        category = get_object_or_404(Category, id=request.POST.get('category_id'))
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('/manage/categories/')

    if request.method == 'POST' and 'delete_category' in request.POST:
        category = get_object_or_404(Category, id=request.POST.get('category_id'))
        category.delete()
        return redirect('/manage/categories/')

    context = {
        'categories': categories,
        'form': form
    }
    return render(request, 'admin/manage_categories.html', context)

def manage_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    product_form = ProductForm()
    category_form = CategoryForm()

    if request.method == 'POST':
        if 'create_product' in request.POST:
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                product_form.save()
                return redirect('/manage/')

        elif 'create_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect('/manage/')

    return render(request, 'admin/manage_products.html', {
        'products': products,
        'categories': categories,
        'product_form': product_form,
        'category_form': category_form,
    })

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('/manage/')
    return render(request, 'admin/edit_form.html', {'form': ProductForm(instance=product)})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('/manage/')


