from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_screenshot, name='user_upload'), 
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('analysis_results/', views.analysis_results, name='analysis_results'),
    path('export_excel/', views.export_excel, name='export_excel'),
]

