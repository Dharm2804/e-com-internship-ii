from email import message
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from . models import Cart, Customer, Order, OrderItem, Product, Wishlist
from . forms import CustomerRegistrationForm , CustomerProfileForm
from django.contrib.auth.views import PasswordChangeView,LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import transaction
# Create your views here.

def home(request):
    return render(request, 'app/home.html')

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request, 'app/contact.html')

class CategoryView(View):
    def get(self, request ,  val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total =Count('title'))
        return render(request, 'app/category.html',locals())
    
class CategoryTitle(View):
    def get(self, request ,  val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, 'app/category.html',locals())

class ProductDetails(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'app/productdetail.html', {'product': product})
    
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerRegistrationForm

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            # return redirect('login')  # Replace 'login' with your actual login page name
        else:
            messages.warning(request, 'Invalid input data')
        return render(request, 'app/customerregistration.html', {'form': form})

class ProfileView(View):
    def get(self, request):
        if hasattr(request.user, 'customer'):  # Check if the user has a profile
            profile = CustomerProfileForm(instance=request.user.customer)  # Pass the profile instance
        else:
            profile = CustomerProfileForm()  # Create a new form if no profile exists
        return render(request, 'app/profile.html', {'profile': profile})
    
    def post(self, request):
        if hasattr(request.user, 'customer'):
            profile = CustomerProfileForm(request.POST, instance=request.user.customer)  # Pass the profile instance
        else:
            profile = CustomerProfileForm(request.POST)  # For new users without a profile
            
        if profile.is_valid():
            profile.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')  # Redirect to profile page
        return render(request, 'app/profile.html', {'profile': profile})
    
class AddressView(View):
    def get(self, request):
        # Get all Customer instances associated with the logged-in user
        addresses = Customer.objects.filter(user=request.user)
        
        if not addresses:
            messages.warning(request, 'No addresses found for this user.')
            return redirect('profile')  # Redirect to the profile page if no addresses are found
        
        return render(request, 'app/address.html', {'addresses': addresses})

class updateAddressView(View):
    def get(self, request, pk):
        address = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(instance=address)
        return render(request, 'app/updateaddress.html', {'form': form})

    def post(self, request, pk):
        address = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully')
            return redirect('address')
        return render(request, 'app/updateaddress.html', {'form': form})
class DeleteAddressView(View):
    def post(self, request, pk):
        address = get_object_or_404(Customer, pk=pk, user=request.user)
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('address')

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'app/changepassword.html'
    success_url = reverse_lazy('profile')  # Redirect to profile instead of login

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)  # Keep user logged in
        messages.success(self.request, 'Your password was successfully changed.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']  # Allow GET and POST requests
    next_page = reverse_lazy('login')

class AddToCartView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If the item already exists, update the quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f"{product.title} has been added to your cart.")
        return redirect('productdetail', pk=pk)

class CartView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to view your cart.')
            return redirect('login')
        
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = sum(item.total_price for item in cart_items)
        
        return render(request, 'app/cart.html', {
            'cart_items': cart_items,
            'total_amount': total_amount
        })

class RemoveFromCartView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
        return redirect('cart')

class AddToWishlistView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        messages.success(request, f"{product.title} has been added to your wishlist.")
        return redirect('productdetail', pk=pk)

class RemoveFromWishlistView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        wishlist_item = get_object_or_404(Wishlist, user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f"{product.title} has been removed from your wishlist.")
        return redirect('wishlist')

class WishlistView(View):
    @method_decorator(login_required)
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items})

class CheckoutView(View):
    @method_decorator(login_required)
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart')
        
        total_amount = sum(item.total_price for item in cart_items)
        addresses = Customer.objects.filter(user=request.user)
        
        return render(request, 'app/checkout.html', {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'addresses': addresses
        })

    @method_decorator(login_required)
    def post(self, request):
        address_id = request.POST.get('address')
        address = get_object_or_404(Customer, id=address_id, user=request.user)
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart')

        total_amount = sum(item.total_price for item in cart_items)

        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                user=request.user,
                customer=address,
                total_amount=total_amount,
                status='Pending'
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.discounted_price
                )

            # Clear the cart
            cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('orders')

class OrdersView(View):
    @method_decorator(login_required)
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
        return render(request, 'app/orders.html', {'orders': orders})

