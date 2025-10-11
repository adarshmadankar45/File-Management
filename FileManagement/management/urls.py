from .views import *
from . import views
from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('Dashboard', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),

    # Master Drawer URLs
    path('search_ward/', views.masterward_list, name='search_ward'),
    path('create_ward/', views.masterward_create, name='create_ward'),
    path('update_ward/<int:pk>/', views.masterward_update, name='update_ward'),
    path('delete_ward/<int:pk>/', views.masterward_delete, name='delete_ward'),

    # Master Drawer URLs
    path('search_drawers/', views.masterdrawer_list, name='search_drawers'),
    path('drawers/create/', views.masterdrawer_create, name='create_drawer'),
    path('drawers/<int:pk>/update/', views.masterdrawer_update, name='update_drawer'),
    path('drawers/<int:pk>/delete/', views.masterdrawer_delete, name='delete_drawer'),

    # Compartment URLs
    path('search_compartments/', views.compartment_list, name='search_compartments'),
    path('compartments/create/', views.compartment_create, name='create_compartment'),
    path('compartments/<int:pk>/update/', views.compartment_update, name='update_compartment'),
    path('compartments/<int:pk>/delete/', views.compartment_delete, name='delete_compartment'),

    path('get-compartments/', views.get_compartments, name='get_compartments'),
    # RevenueSite URLs
    path('merge-files/', merge_files_view, name='merge_files'),
    path('create/', RevenueSiteCreateView.as_view(), name='create'),
    path('list/', RevenueSiteListView.as_view(), name='list'),
    path('<int:pk>/', RevenueSiteDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', RevenueSiteUpdateView.as_view(), name='update'),
    path('revenuesite/<int:pk>/delete/', views.revenuesite_delete, name='revenuesite_delete'),
    path('register/', register, name='register'),
    path('merge-documents/', merge_documents, name='merge_documents'),
    path('<int:pk>/unmerge/', unmerge_document, name='unmerge'),
    path('<int:pk>/unmerge/options/', unmerge_options, name='unmerge_options'),
    path('<int:pk>/unmerge/selected/', unmerge_selected, name='unmerge_selected'),
    path('upload-documents/<int:pk>/', views.upload_documents, name='upload_documents'),

    path('update-additional-documents/', views.update_additional_documents, name='update_additional_documents'),

    path('site/<int:pk>/qr-data/', generate_qr_code, name='qr_code_data'),
    path('generate-all-qr-pdf/', generate_all_qr_pdf, name='generate_all_qr_pdf'),
    path('generate-selected-qr-pdf/', generate_selected_qr_pdf, name='generate_selected_qr_pdf'),
    path('get-qr-preview-data', get_qr_preview_data, name='get_qr_preview_data'),
    path('get-qr-preview-data/', get_qr_preview_data, name='get_qr_preview_data'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        extra_context={'title': ('लॉगिन / Login')}
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)