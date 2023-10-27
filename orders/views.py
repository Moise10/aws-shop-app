from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.conf import settings
import weasyprint
from weasyprint import HTML, CSS
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created



@staff_member_required
def admin_order_pdf(request, order_id):
  order = get_object_or_404(Order, id=order_id)
  html = render_to_string('orders/order/pdf.html', {'order': order})
  
  # Define the URL for the CSS file
  css_url = settings.STATIC_URL + 'css/pdf.css'

  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
  
  # Use WeasyPrint's CSS function with the URL
  css = CSS(string=f"@page {{ size: A4; }} {css_url}")
  
  # Use the CSS in the HTML rendering
  # HTML(string=html).write_pdf(response, stylesheets=[css])
  weasyprint.HTML(string=html).write_pdf(response,
                            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')])

  return response


def order_create(request):

  cart = Cart(request)
  if request.method == "POST":
    form = OrderCreateForm(request.POST)
    if form.is_valid():
      order = form.save()
      for item in cart:
        OrderItem.objects.create(order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity'])
      #clear the cart
      cart.clear()
      # launch asynchronous task
      order_created.delay(order.id)
      # set the order in the session
      request.session['order_id'] = order.id
      # redirect for payment
    return redirect(reverse('payment:process'))
  else:
    form = OrderCreateForm()
  return render(request,'orders/order/create.html',
                      {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
  order = get_object_or_404(Order, id=order_id)
  return render(request,
              'admin/orders/order/detail.html',
              {'order': order})


