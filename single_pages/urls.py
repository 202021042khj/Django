from django.urls import path, include 
from  .import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('blog/', include('blog.urls')),
    path('about_me/', views.about_me),
    path('', views.landing ), #127.0.0.1:8000
]