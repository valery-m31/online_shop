from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Item, OrderItem, Order, UserProfile, Category
from .forms import CreateAddressForm
from .tasks import send_order_email


class CategoryView(ListView):
    model = Category
    template_name = 'shop/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ItemListView(ListView):
    model = Item
    paginate_by = 12
    ordering = ['id']
    template_name = 'shop/item_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list = Category.objects.all()
        context['category_list'] = category_list
        context['best_items'] = Item.objects.all()[0:6]
        return context


def by_category(request, category):
    """select items by category"""
    category_item = get_object_or_404(Category, name=category)
    category_list = Category.objects.all()
    items_by_category = Item.objects.filter(
        category=category_item
        ).order_by('title')
    paginator = Paginator(items_by_category, 8)
    page = request.GET.get('page')
    try:
        items_by_category = paginator.page(page)
    except PageNotAnInteger:
        items_by_category = paginator.page(1)
    except EmptyPage:
        items_by_category = paginator.page(paginator.num_pages)
    return render(request, 'shop/item_list_by_category.html', {
        'category': category,
        'items_by_category': items_by_category,
        'category_list': category_list,
        })


class ItemDetailView(DetailView):
    model = Item
    context_object_name = 'item'

    def get(self, request, slug): #deleted *args and **kwargs
        """select info from db about item"""
        item = get_object_or_404(Item, slug=slug)
        category_list = Category.objects.all()
        context = {
            'item': item,
            'category_list': category_list
        }
        return render(request, 'shop/item_detail.html', context)


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            order = Order.objects.filter(
                user_id=request.user.id,
                ordered=True
                ).order_by('id')
            category_list = Category.objects.all()
            len_order = len(order)
            context = {
                'objects': order,
                'len_order': len_order,
                'category_list': category_list
            }
            return render(self.request, 'shop/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            order_item = OrderItem.objects.filter(
                user__id=request.user.id,
                ordered=False
                ).order_by('item')
            category_list = Category.objects.all()
            total_sum = 0
            for item in order_item:
                total_sum += item.sum_total_price()
            context = {
                'order_item': order_item,
                'total_sum': round(total_sum, 2),
                'category_list': category_list
            }
            return render(self.request, 'shop/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "you do not have items in the cart")
            return redirect("/")


class CreateOrderAddressFormView(LoginRequiredMixin, CreateView):

    def get(self, request):
        form = CreateAddressForm()
        category_list = Category.objects.all()
        context = {
            'form': form,
            'category_list': category_list
        }
        return render(request, 'shop/create_address.html', context)

    @staticmethod
    def get_email_info(order_list):
        titles = [item.item.title for item in order_list]
        prices = [item.item.discount_price if item.item.discount_price \
            else item.item.price for item in order_list]
        quantity = [item.quantity for item in order_list]
        sum_total = [item.quantity * item.item.discount_price if \
            item.item.discount_price else item.item.price \
            for item in order_list]
        return titles, prices, quantity, sum_total

    def post(self, request):
        if request.method == 'POST':
            bound_form = CreateAddressForm(request.POST)
            if bound_form.is_valid():
                new_address = bound_form.save(commit=False)
                new_address.user = UserProfile.objects.get(
                    id=self.request.user.id
                    )
                new_address.save()
                bound_form.save_m2m()
                order = Order.objects.get(
                    user__id=self.request.user.id, ordered=False
                    )
                order.address = new_address
                order.ordered = True
                order.save()
                order_list = order.items.all()
                to_email = order.address.email
                title, price, quantity, sum_total = \
                    CreateOrderAddressFormView.get_email_info(order_list)
                send_order_email(to_email, title, price, quantity, sum_total)
                items = OrderItem.objects.filter(user__id=self.request.user.id)
                for item in items:
                    item.ordered = True
                    item.save()
                return success_order_view(request)
        return render(
            request,
            'shop/create_address.html',
            context={'form': bound_form}
            )


@login_required
def success_order_view(request):
    category_list = Category.objects.all()
    context = {
        'category_list': category_list
    }
    return render(request, 'shop/success_order.html', context)


@login_required
def add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=UserProfile.objects.get(id=request.user.id),
        ordered=False
    )
    order_qs = Order.objects.filter(user__id=request.user.id, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.items.add(order_item)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=UserProfile.objects.get(id=request.user.id),
            ordered_date=ordered_date
            )
        order.items.add(order_item)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_item_from_cart(request, slug):

    OrderItem.objects.get(
        item__slug=slug,
        user__id=request.user.id,
        ordered=False
        ).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_one_item(request, slug):
    item = get_object_or_404(
        OrderItem,
        item__slug=slug,
        user__id=request.user.id,
        ordered=False
        )
    if item.quantity > 1:
        item.quantity = item.quantity - 1
        item.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if item.quantity == 1:
        remove_item_from_cart(request, slug)


@login_required
def add_one_item(request, slug):
    item = OrderItem.objects.get(
        item__slug=slug,
        user_id=request.user.id,
        ordered=False
        )
    item.quantity += 1
    item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
