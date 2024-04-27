from typing import Optional

from .models import Cart


def get_or_set_order_session(request) -> Cart:
    order_id: Optional[int] = request.session.get('order_id', None)
    if order_id is not None:
        order, _ = Cart.objects.get_or_create(id=order_id, ordered=False)
        request.session['order_id'] = order.id
    else:
        order = Cart.objects.create()
        request.session['order_id'] = order.id

    if request.user.is_authenticated and order.user is None:
        order.user = request.user
        order.save(update_fields=['user', ])
    return order


__all__ = ('get_or_set_order_session',)