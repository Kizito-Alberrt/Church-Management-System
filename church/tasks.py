# church/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import News, User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_news_notification_task(news_id):
    try:
        news = News.objects.get(pk=news_id)
        
        # Determine which users should receive this news
        if news.target_audience == 'ALL':
            recipients = User.objects.filter(is_active=True)
        elif news.target_audience == 'REVERENDS':
            recipients = User.objects.filter(
                Q(role='MAIN_REVEREND') | Q(role='ADMIN') | Q(is_superuser=True),
                is_active=True
            )
        elif news.target_audience == 'PASTORS':
            recipients = User.objects.filter(
                Q(role='PASTOR') | Q(role='MAIN_REVEREND') | Q(role='ADMIN') | Q(is_superuser=True),
                is_active=True
            )
        else:
            recipients = User.objects.none()
        
        # Prepare email content
        subject = f"New Announcement: {news.title}"
        html_content = render_to_string('church/news/email_notification.html', {
            'news': news,
            'site_name': 'Church Management System'
        })
        text_content = strip_tags(html_content)
        
        # Send emails
        for user in recipients:
            if user.email:
                try:
                    msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as e:
                    logger.error(f"Failed to send news email to {user.email}: {str(e)}")
        
        # Update news record
        news.emails_sent = True
        news.email_sent_at = timezone.now()
        news.save()
        
    except News.DoesNotExist:
        logger.error(f"News with id {news_id} does not exist")
    except Exception as e:
        logger.error(f"Error in send_news_notification_task: {str(e)}")