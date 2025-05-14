from django.contrib import admin
from django.urls import path
from Shonchoy import views 

urlpatterns = [
    path('', views.webpage, name='webpage_root'),  
    path('webpage/', views.webpage, name='webpage'), 
    path('admin/', admin.site.urls),
    path('homepage/', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signupsuccessful/', views.signupsuccessful, name='signupsuccessful'),
    path('home/', views.home, name='home'),
    path('mybank/', views.mybank, name='mybank'),
    path('loaninquiries/', views.loaninquiries, name='loaninquiries'),
    path('notifications/', views.notifications, name='notifications'),
    path('chartlist/', views.chartlist, name='chartlist'),
    path('currentstatus/', views.currentstatus, name='currentstatus'),
    path('transaction/', views.transaction, name='transaction'),
    path('myloans/', views.myloans, name='myloans'),
    path('logout/', views.logout, name='logout'),

]
