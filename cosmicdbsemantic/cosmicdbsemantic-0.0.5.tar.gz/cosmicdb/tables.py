import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.urls import reverse


class NotificationTable(tables.Table):
    read = tables.Column(attrs={'th': {'class': 'read_column',}}, order_by='read')
    short_notification = tables.Column(verbose_name="Message", order_by='notification')
    created_at = tables.Column(verbose_name="Received At")
    def render_read(self, record):
        html = '<i class="envelope icon"></i>'
        if record.read:
            html = '<i class="envelope outline icon"></i>'
        return mark_safe(html)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        row_onclick = "temp_url = '"+reverse('notifications', args=[0])+"';var url = temp_url.substr(0,temp_url.length-2)+$(this).data('id')+'/';window.location.href = url;"
        self.row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': mark_safe(row_onclick),
            'class': 'table-row',
        }
    class Meta:
        empty_text = "No notifications"
