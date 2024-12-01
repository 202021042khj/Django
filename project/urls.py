from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),  # Product 리스트
    path('search/', views.product_search, name='product_search'),
    
    path('youtube_comment_crawler/', views.youtube_comment_crawler, name='youtube_comment_crawler'),
    path('process_csv/', views.process_local_csv, name='process_csv'),  # 로컬 CSV 처리
]
