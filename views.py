
from django.views import generic
from django.views.generic import DetailView

from django.shortcuts import render, redirect ,get_object_or_404
from burger.models import Burger
from .models import Cart ,CartItem

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

a =0
def home_page_view(request):
    last_three_burger = Burger.objects.all().order_by('published_time')[:3]
    context = {
        'three_burger': last_three_burger,
    }
    return render(request, 'burger/home.html', context=context)


class AboutPageGenericView(generic.TemplateView):
    template_name = 'burger/about.html'


class NewsPageGenericView(generic.TemplateView):
    template_name = 'burger/news.html'


class NewsDetailPageGenericView(generic.TemplateView):
    template_name = 'burger/single-news.html'


def shop_page_view(request):
    all_burgers = Burger.objects.all().order_by('published_time')
    context = {
        'burgers': all_burgers
    }
    return render(request, 'burger/shop.html', context=context)


class ProductDetailPageGenericView(DetailView):
    model = Burger
    template_name = 'burger/single-product.html'


class ContactPageGenericView(generic.TemplateView):
    template_name = 'burger/contact.html'


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Burger.objects.get(id=product_id)
    if current_user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=current_user, product=product)
            cart_item.quantity += 1
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )

        cart_item.save()

        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:

        product = get_object_or_404(Burger, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=current_user)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1

            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Burger, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')


def remove_cart_item(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Burger, id=product_id)
        cart_item = CartItem.objects.get(product=product, user=current_user)
        cart_item.delete()

        return redirect('cart')
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Burger, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()

        return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'burger/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None, ):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'burger/checkout.html', context)


