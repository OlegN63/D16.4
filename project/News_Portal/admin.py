from django.contrib import admin
from .models import Post, Category


# создаём новый класс для представления новостей в админке
class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = [field.name for field in Post._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    #list_display = ('name', 'price') # оставляем только нужные для отображения столбцы
    #list_filter = ('price', 'quantity', 'name') # добавляем примитивные фильтры в нашу админку

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
#admin.site.unregister(Post) # разрегистрируем наши новости
