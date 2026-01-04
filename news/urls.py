from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/articles/', views.dashboard_article_list, name='dashboard_article_list'),
    path('dashboard/articles/new/', views.dashboard_article_create, name='dashboard_article_create'),
    path('dashboard/articles/<int:pk>/edit/', views.dashboard_article_edit, name='dashboard_article_edit'),
    path('dashboard/articles/<int:pk>/delete/', views.dashboard_article_delete, name='dashboard_article_delete'),
    
    path('dashboard/categories/', views.dashboard_category_list, name='dashboard_category_list'),
    path('dashboard/categories/new/', views.dashboard_category_create, name='dashboard_category_create'),
    path('dashboard/categories/<int:pk>/edit/', views.dashboard_category_edit, name='dashboard_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.dashboard_category_delete, name='dashboard_category_delete'),
    
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/breaking-news/', views.dashboard_breaking_news, name='dashboard_breaking_news'),
]
