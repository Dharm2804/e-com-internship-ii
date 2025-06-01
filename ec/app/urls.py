from django.urls import path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordChangeForm, LoginForm 

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('category/<slug:val>', views.CategoryView.as_view(), name='category'),
    path('category-title/<val>', views.CategoryTitle.as_view(), name='category-title'),
    path('product/<int:pk>/', views.ProductDetails.as_view(), name='productdetail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    path('address/', views.AddressView.as_view(), name='address'),
    path('update_address/<int:pk>/', views.updateAddressView.as_view(), name='updateaddress'),
    
    path('delete_address/<int:pk>/', views.DeleteAddressView.as_view(), name='deleteaddress'),
    
    path('add-to-cart/<int:pk>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('remove-from-cart/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    path('add-to-wishlist/<int:pk>/', views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove-from-wishlist/<int:pk>/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrdersView.as_view(), name='orders'),
    
    path('changepassword/', views.CustomPasswordChangeView.as_view(), name='changepassword'),
    
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
    path('account/login/', auth_views.LoginView.as_view(
    template_name='app/login.html',
    authentication_form=LoginForm  # Correct reference to LoginForm
    ), name='login'),
    path('account/logout/', views.CustomLogoutView.as_view(), name='logout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
