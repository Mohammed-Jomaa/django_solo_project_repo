from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('create_user',views.create_user,name='create_user'),
    path('login_user',views.login_user,name ='login_user'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('logout',views.logout,name='logout'),
    path('new_family',views.new_family,name='new_family'),
    path('create_family',views.create_family,name='create_family'),
    path('manage_family/<int:id>',views.manage_family,name='manage_family'),
    path('manage_family/add_admin',views.add_admin,name='add_admin'),
    path('family/<int:id>/tasks', views.task_list, name='task_list'),
    path('family/<int:id>/review_tasks', views.review_tasks, name='review_tasks'),
    path('family/<int:id>/children', views.children, name='children'),
    path('family/<int:id>/rewards', views.rewards, name='rewards'),
    path('delete_family/', views.delete_family, name='delete_family'),
    path('family/<int:id>/tasks/add/', views.add_task, name='add_task'),
    path('family/tasks/delete/<int:id>/', views.delete_task, name='delete_task'),
    path('family/<int:id>/children/add/', views.create_child, name='create_child'),
    path('family/<int:id>/children/create_child/add', views.add_child, name='add_child'),
    path('family/<int:id>/rewards/create/', views.create_reward, name='create_reward'),
    path('family/<int:id>/rewards/add/', views.add_reward, name='add_reward'),
    path('family/rewards/delete/<int:id>/', views.delete_reward, name='delete_reward'),





    
]
