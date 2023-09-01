from django_filters import FilterSet, ModelMultipleChoiceFilter, CharFilter, DateFilter, DateTimeFilter
from .models import Post
from django import forms

# Создаем свой набор фильтров для модели Post.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class PostFilter(FilterSet):
    header = CharFilter(lookup_expr='icontains', label='По заголовку')
    #author__user__username = CharFilter(lookup_expr='icontains', label='По имени автора')
    author = CharFilter(lookup_expr='icontains', label='По имени автора')
    time_in = DateFilter(#DateTimeFilter(
        field_name='created_at',
        lookup_expr='gt',
        label='Позже указанной даты',
        #widget=forms.DateTimeInput(attrs={'type': 'DATETIME'})
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['header', 'author', 'time_in']


'''    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
            # поиск по заголовку
            'header': ['icontains'],
            # по автору
            'author__user__username': ['icontains'],
            # позже указываемой даты
            'time_in': ['gt'],
        }
'''
'''
    header_filter = ModelMultipleChoiceFilter(field_name='header',
                                              lookup_expr='icontains',
                                              label='По заголовку',
                                              conjoined=True)
    author_filter = ModelMultipleChoiceFilter(field_name='author__user__username',
                                              lookup_expr='icontains',
                                              label='По автору',
                                              conjoined=True)
    date_filter = ModelMultipleChoiceFilter(field_name='created_datetime',
                                            lookup_expr='gt',
                                            label='Опубликовано позднее',
                                            conjoined=True)

    class Meta:
        model = Post
        fields = (
            'header_filter',
            'author_filter',
            'date_filter',
        )
'''
