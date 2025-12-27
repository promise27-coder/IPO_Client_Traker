from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Main Dashboard ---
    path('', views.dashboard, name='dashboard'),
    
    # --- Client Operations ---
    path('add/', views.add_client, name='add_client'),
    path('detail/<int:id>/', views.client_detail, name='client_detail'),
    path('update-cell/<int:id>/', views.update_client_cell, name='update_client_cell'),
    
    # --- Master List Operations ---
    # (Alag page hatavi didhu, have khali update and add nu logic che)
    path('add-master-inline/', views.add_master_entry, name='add_master_entry'),
    path('update-master/<int:id>/', views.update_master_cell, name='update_master_cell'),
    path('import/<int:ipo_id>/', views.import_from_master, name='import_from_master'),
    
    # --- IPO Operations ---
    path('add-ipo/', views.add_ipo, name='add_ipo'),
    
    # --- Auth ---
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]