from django.urls import path
from .views import TaskList, TaskDetail,CustomLoginView, TaskCreate, TaskUpdate, DeleteView, TaskReorder
from django.contrib.auth.views import LogoutView
from . import views
# from .views import deleteAll


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    
    path("register", views.register, name="register"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    # path("login",views.login, name="login"),
    path("logout",views.logout,name="logout"),
    path('deletecomplete', views.deleteCompleted, name='deletecomplete'),
    path('', TaskList.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteView.as_view(), name='task-delete'),
    path('task-reorder/', TaskReorder.as_view(), name='task-reorder'),
]
