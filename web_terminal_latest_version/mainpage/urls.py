from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('timesfm/', views.timesfmweb, name='timesfmweb'),
    path('account/', views.account, name='account'),
    path('analysis/', views.analysis, name='analysis'),
    path('backward-test/', views.backwardtest, name='backwardtest'),
    path('setting/', views.setting, name='setting'),    
]
