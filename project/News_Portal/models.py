from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        author_article_rating = 0
        author_comment_rating = 0
        author_article_comment_rating = 0

        author_article_rating = Post.objects.filter(author=self).aggregate(Sum('rating'))['rating_sum']*3
        author_comment_rating = Comment.objects.filter(user=self.user).aggregate(Sum('rating'))['rating_sum']
        author_article_comment_rating = Comment.objects.filter(post_author_user=self.user).aggregate(Sum('rating'))['rating_sum']

        self.rating = author_article_rating + author_comment_rating + author_article_comment_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True) #название категории. Поле должно быть уникальным (в определении поля необходимо написать параметр unique = True)
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True)

    def subscribe(self):
        pass

    def __str__(self):
        return self.name.title()


class Post(models.Model):
    article = 'AR'
    news = 'NE'

    POST_TYPES = [
        (article, 'статья'),
        (news, 'новость')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)#связь «один ко многим» с моделью Author;
    type = models.CharField(max_length=2, choices=POST_TYPES, default=article)#поле с выбором — «статья» или «новость»;
    time_in = models.DateTimeField(auto_now_add=True)#автоматически добавляемая дата и время создания;
    category = models.ManyToManyField(Category, through='PostCategory')#связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
    header = models.CharField(max_length=255, default='заголовок')#заголовок статьи/новости;
    text = models.TextField(default='текст статьи/новости')#текст статьи/новости;
    _rating = models.IntegerField(default=0, db_column='rating')#рейтинг статьи/новости.

    def __str__(self):
        return f'{self.header.title()}: {self.text[:20]}'

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = int(value) if value >= 0 else 0
        self.save()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        text = str(self.text)
        if len(text) >= 124:
            return "%s..." % text
        preview = text.split()[:125]
        return "%s..." % preview

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    #добавляем кэширование пока не изменится новость
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'product-{self.pk}') # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) #связь «один ко многим» с моделью Post;
    category = models.ForeignKey(Category, on_delete=models.CASCADE) #связь «один ко многим» с моделью Category.


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) #связь «один ко многим» с моделью Post;
    user = models.ForeignKey(User, on_delete=models.CASCADE) #связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь, необязательно автор);
    text = models.TextField(default='текст комментария') #текст комментария;
    time_in = models.DateTimeField(auto_now_add=True) #дата и время создания комментария;
    _rating = models.IntegerField(default=0, db_column='rating') #рейтинг комментария.

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = int(value) if value >= 0 else 0
        self.save()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()