from django.db import models
from django.utils.translation import ugettext_lazy as _


class Answer(models.Model):
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.answer[:25]


class Category(models.Model):
    name = models.CharField(max_length=22)
    display_all = models.BooleanField(default=False)
    display_factor = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Question(models.Model):

    QUESTION_TYPE_MULTIPLE = _('Multiplechoice')
    QUESTION_TYPE_SINGLE = _('Singlechoice')
    QUESTION_TYPE_TEXT = _('Textfield')
    QUESTION_TYPE_SCALA = _('Scala')

    QUESTION_TYPES = (
        (_('Multiplechoice'), QUESTION_TYPE_MULTIPLE),
        (_('Singlechoice'), QUESTION_TYPE_SINGLE),
        (_('Textfield'), QUESTION_TYPE_TEXT),
        (_('Scala'), QUESTION_TYPE_SCALA),
    )

    number_rage_help = _('Only required for Scala-Fields. ')
    description_help = _('Only required if you want to display a description.')
    question = models.CharField(max_length=255, verbose_name=_('Question'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    answers = models.ManyToManyField(Answer, blank=True)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=QUESTION_TYPE_TEXT, verbose_name=_('Type'))
    category = models.ForeignKey(verbose_name=_('Category'), to=Category, on_delete=models.CASCADE)
    number_range_end = models.IntegerField(help_text=number_rage_help, default=0)
    count = models.PositiveIntegerField(default=0)
    description = models.CharField(null=True, blank=True, max_length=255, help_text=description_help)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.question

    def get_answers(self):
        return self.answers.all()


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.answer

    @property
    def type(self):
        return self.question.type
