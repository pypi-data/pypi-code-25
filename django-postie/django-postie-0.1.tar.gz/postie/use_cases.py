from django.conf import settings

from .tasks import send_letter

__all__ = (
    'SendMailUseCase',
)


class SendMailUseCase:
    """
    Send email use case. Used to send email, duh.
    """
    
    def execute(self, letter):
        if getattr(settings, 'POSTIE_INSTANT_SEND', True):
            return send_letter(letter.object.id)
        else:
            send_letter.delay(letter.object.id)
            
            return None
