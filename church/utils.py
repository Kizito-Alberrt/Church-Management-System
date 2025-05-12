from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import User, Worshiper

def send_welcome_email(obj, recipient_email, language='en'):
    """
    Send a welcome email to a new user or worshiper.
    
    Args:
        obj: User or Worshiper object
        recipient_email: Email address to send the email to
        language: Language code ('en' or 'pt')
    """
    # Set the language for translation
    from django.utils import translation
    translation.activate(language)

    # Determine user name
    if isinstance(obj, User):
        user_name = obj.get_full_name() or obj.username
        role_key = obj.role
    elif isinstance(obj, Worshiper):
        user_name = f"{obj.first_name} {obj.last_name}".strip()
        role_key = 'WORSHIPER'
    else:
        raise ValueError("Object must be a User or Worshiper")

    # Map role keys to display names (translated)
    role_display_map = {
        'ADMIN': _('Admin'),
        'MAIN_REVEREND': _('Main Reverend'),
        'PASTOR': _('Pastor'),
        'WORSHIPER': _('Worshiper'),
    }
    user_role = role_display_map.get(role_key, _('Member'))

    # Use a constant for system name
    system_name = getattr(settings, 'SYSTEM_NAME', 'Church Management System')

    subject = _('Welcome to the Church Management System')
    
    # Prepare context for the email template
    context = {
        'user_name': user_name,
        'user_role': user_role,
        'system_name': system_name,
        'login_url': f"{settings.SITE_URL}{settings.LOGIN_URL}",
    }
    
    # Render HTML and plain text versions of the email
    html_message = render_to_string('church/emails/welcome_email.html', context)
    plain_message = render_to_string('church/emails/welcome_email.txt', context)
    
    # Send the email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send welcome email to {recipient_email}: {str(e)}")
    
    # Reset language to default
    translation.deactivate()