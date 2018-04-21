from django.core.mail import send_mail
import structlog

from .merge import MergedEmail

logger = structlog.get_logger()


def send(email: MergedEmail, recipient: str) -> int:
    """
    A helper to send the merged email to a single recipient, from DEFAULT_FROM_EMAIL

    Returns the number of emails sent (because we only allow one recipient, the maximum is 1).
    """
    logger.info('sending-transactional-email', template=email.template, recipient=recipient)
    return send_mail(
        subject=email.subject,
        message=email.plain,
        html_message=email.html,
        from_email=None,
        recipient_list=[recipient],
    )
