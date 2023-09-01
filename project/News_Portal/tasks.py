import datetime
from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string

from .models import Post, Category
from django.core.mail import EmailMultiAlternatives


@shared_task
def week_send_email_task():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=last_week)
    categories = set(posts.values_list('category__name_category', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.EMAIL_HOST_USER_FULL,
        bcc=subscribers
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def send_email_task(pk):
    posts = Post.objects.get(pk=pk)
    category = [cat for cat in posts[0].category.all()]
    header = posts[0].header
    subscribers_emails = []

    for cat in category:
        subscribers = cat.subscribers.all()
        subscribers_emails += [s.email for s in subscribers]

    html_content = render_to_string(
        'post_created_email.html',
        {
            'link': f'{settings.SITE_URL}/news/{pk}',
            'text': posts[0].preview,
        }
    )
    msg = EmailMultiAlternatives(
        subject=header,
        body='',
        from_email=settings.EMAIL_HOST_USER_FULL,
        bcc=subscribers_emails
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
