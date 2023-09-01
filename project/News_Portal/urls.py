from django.urls import path
# Импортируем созданное нами представление
from .views import (NewsList, NewsDetail, NewsSearch, NewsCreate, NewsUpdate, NewsDelete, CategoryListView, subscribe,
                    unsubscribe)
from django.views.decorators.cache import cache_page


urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем новостям у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   #path('', cache_page(60)(NewsList.as_view()), name='post_List'),# страница кэшируется 60 сек
   path('', NewsList.as_view(), name='post_List'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   #path('<int:pk>', cache_page(300)(NewsDetail.as_view()), name='post_detail'),# страница кэшируется 300 сек
   path('<int:pk>', NewsDetail.as_view(), name='post_detail'),
   path('search/', NewsSearch.as_view(), name='post_search'),
   path('create/', NewsCreate.as_view(), name='post_create'),
   path('<int:pk>/edit/', NewsUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', NewsDelete.as_view(), name='post_delete'),

   path('article/create/', NewsCreate.as_view(), name='post_create'),
   path('article/<int:pk>/edit/', NewsUpdate.as_view(), name='post_update'),
   path('article/<int:pk>/delete/', NewsDelete.as_view(), name='post_delete'),
   path('categories/<int:pk>/', CategoryListView.as_view(), name='category_list'),
   path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
   path('categories/<int:pk>/unsubscribe', unsubscribe, name='unsubscribe'),
]