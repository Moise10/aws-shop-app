from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
  category = None
  categories = Category.objects.all()
  products = Product.objects.filter(available=True)
  if category_slug:
    category = get_object_or_404(Category, slug=category_slug)
    products = product.filter(category=category)
  return render(request, 'shop/product/list.html',
                  {'category': category, 'products': products,
                  'categories': categories})


def product_detail(request, id, slug):
  product = get_object_or_404(
                      Product, slug=slug, id=id, 
                      available=True)
  cart_product_form = CartAddProductForm()
  return render(request, 
              'shop/product/detail.html',
              {'product': product,
              'cart_product_form': cart_product_form})
              




  


