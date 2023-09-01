# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import Post, Category
from datetime import datetime
from pprint import pprint
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from .tasks import send_email_task
from django.core.cache import cache # импортируем наш кэш


class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = ['-time_in']
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10  # вот так мы можем указать количество записей на странице
    # Переопределяем функцию получения списка товаров

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context
    '''def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        pprint(context)
        return context'''


class NewsDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs): # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'product-{self.kwargs["pk"]}', None) # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.
        #если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
           obj = super().get_object(queryset=self.queryset)
           cache.set(f'product-{self.kwargs["pk"]}', obj)
        return obj

class NewsSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'post_search'
    ordering = ['-time_in']
    paginate_by = 5

    # Переопределяем функцию получения списка новостей
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список новостей
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        pprint(context)
        return context

# Добавляем новое представление для создания товаров.
class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('News_Portal.add_post', )
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'news' in self.request.path:
            post_type = 'NE'
        elif 'article' in self.request.path:
            post_type = 'AR'
        self.object.post_type = post_type
        form.instance.author = self.request.user.author
        self.object.save()
        send_email_task.delay(self.object.pk)
        return super().form_valid(form)

# Добавляем представление для изменения товара.
class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('News_Portal.change_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

# Представление удаляющее товар.
class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-time_in')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы подписались на рассылку новостей категории'
    return render(request, 'subscribe.html', {'category': category, 'message': message})


# !!!Не работает, т.к. нету личнго кабинета (http://127.0.0.1:8000/accounts/profile/)
# !!!ОТПИСАТЬСЯ НЕ ПОЛУЧИТСЯ
@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return render(request, 'subscribe.html')
# !!!ОТПИСАТЬСЯ НЕ ПОЛУЧИТСЯ