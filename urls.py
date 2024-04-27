from django.urls import path

from burger.views import home_page_view, AboutPageGenericView, NewsPageGenericView, shop_page_view, \
    ContactView, NewsDetailPageGenericView, ProductDetailPageGenericView, cart, add_cart, remove_cart, \
    remove_cart_item, checkout

urlpatterns = [
    path('', home_page_view, name='home'),
    path('about/', AboutPageGenericView.as_view(), name='about'),
    path('shop/', shop_page_view, name='shop'),
    path('shop/<int:pk>', ProductDetailPageGenericView.as_view(), name='product-detail'),
    path('news/', NewsPageGenericView.as_view(), name='news'),
    path('news/detail/', NewsDetailPageGenericView.as_view(), name='news-detail'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('cart', cart, name='cart'),
    path('add_cart/<int:product_id>/', add_cart, name='add-cart'),
    path('remove_cart/<int:product_id>/', remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', remove_cart_item, name='remove_cart_item'),
    path('checkout/', checkout, name='checkout'),
]
