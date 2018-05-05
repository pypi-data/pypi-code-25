from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import Question, Answer, UserAnswer, Category


class QuestionDashboard(Question):
    class Meta:
        proxy = True


class QuestionDashboardAdmin(admin.ModelAdmin):
    list_display = ('question', )

    def get_changelist(self, request, **kwargs):
        return super(QuestionDashboardAdmin, self).get_changelist(request)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'get_obj_url')
    fields = ('question', 'description', 'is_active', 'answers', 'type', 'category', 'number_range_end', 'count')

    readonly_fields = ('count', )

    def get_obj_url(self, obj):
        return format_html('<a href="{0}">Edit</a>',
                           reverse('admin:poll_question_change', args=(obj.pk, ), current_app='poll'))

    get_obj_url.allow_tags = True
    get_obj_url.short_description = _('Actions')


class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('answer', 'type')
    list_filter = ('question__type', )


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Category)
admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(QuestionDashboard, QuestionDashboardAdmin)
