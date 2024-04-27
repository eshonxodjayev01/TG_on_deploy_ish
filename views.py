from asyncio.log import logger
from email.message import EmailMessage
from pyexpat.errors import messages
from typing import Dict, Any

from django.shortcuts import reverse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.views import generic
from django.views.generic import DetailView

from django.shortcuts import render, redirect, get_object_or_404
from stripe import LineItem

from accounts.models import Account
from burger.models import Burger, StripePayment, Payment, Order
from config import settings
from .forms import ContactForm, StripePaymentForm, CheckoutForm
from .models import Cart, CartItem

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import datetime
import json
from logging import getLogger
from typing import Any, Dict, Union, List

import stripe
from django.conf import settings
from django.contrib import messages

from django.http import JsonResponse
from django.shortcuts import (get_object_or_404, reverse, redirect)

from django.views import generic

from .utils import get_or_set_order_session


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


class ContactView(generic.FormView):
    template_name: str = 'burger/contact.html'
    form_class = ContactForm

    def get_success_url(self) -> str:
        return reverse("contact")

    def form_valid(self, form):
        messages.info(
            self.request, "Thanks for getting in touch. We have received your message."
        )
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')

        full_message = f"""
            Received message below from {name}, {email}
            ________________________


            {message}
            """
        send_mail(
            subject="Received contact form submission",
            message=full_message,

        )
        return super(ContactView, self).form_valid(form)


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


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            """reset password"""
            current_site = get_current_site(request)
            mail_subject = "Please reset your password"
            message = render_to_string('accounts/reset_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)

            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'password reset email has been sent')
            return redirect('login')

        else:
            messages.error(request, 'account dose not exists')
            return redirect('forgot-password')

    return render(request, 'accounts/forgotPassword.html')


def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):

        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'reset your password')
        return redirect('reset-password')
    else:
        messages.error(request, 'this link has expired')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'password has been reset')
            return redirect('login')

        else:
            messages.error(request, 'password do not match')
            return redirect('reset-password')
    else:
        return render(request, 'accounts/resetPassword.html')


def checkout(request, total=0, total_price=0, quantity=0, cart_items=None):
    tax = 0.00
    handing = 0.00
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        total = total_price + 10

    except ObjectDoesNotExist:
        pass  # just ignore

    tax = round(((2 * total_price) / 100), 2)
    grand_total = total_price + tax
    handing = 15.00
    total = float(grand_total) + handing

    context = {
        'total_price': total_price,
        'quantity': quantity,
        'cart_items': cart_items,
        'handing': handing,
        'vat': tax,
        'order_total': total,
    }

    return render(request, 'burger/checkout.html')






