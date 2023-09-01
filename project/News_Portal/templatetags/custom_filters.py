from django import template

register = template.Library()

bad_words = ['дурак', 'идиот', 'дура', 'идиотка']

# Регистрируем наш фильтр под именем censor, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def censor(text: str):
    for bad_word in bad_words:
        text = text.lower().replace(bad_word.lower(), '*****')
    return text

# для проверки кэшировния делаем как в скринкасте
@register.filter()
def pow(value, pow):
    return value**pow