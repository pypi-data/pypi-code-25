from itertools import chain

from poll.models import Question, Answer, Category
from django import forms
from django.forms import widgets
from poll.forms import SingleChoiceForm, MultipleChoiceForm, TextfieldForm


def get_questions():
    questions = Question.objects.filter(is_active=True).order_by('count')
    categories = Category.objects.all()
    question_list = list()
    for cat in categories:
        if cat.display_all:
            cat_question = questions.filter(category__name__exact=cat.name)
        else:
            cat_question = questions.filter(category__name__exact=cat.name)[:cat.display_factor]
        question_list = list(chain(question_list, cat_question))

    return question_list


def get_html_form(ques, form):
    html = ''

    for i in range(len(form.fields)):
        inp = ''
        if ques[i].type == Question.QUESTION_TYPE_MULTIPLE:
            inp = '<select id="id_answer'+str(i+1) + '" name="answer'+str(i+1)+'" multiple="multiple">'
            ans = Question.objects.get(pk=ques[i].id).get_answers()
            for q in range(len(ans)):
                inp += '<option value="'+str(ans[q].pk)+'">'+ans[q].answer+'</option>'
            inp += '</select>'
        elif ques[i].type == Question.QUESTION_TYPE_SINGLE:
            inp = '<select id="id_answer'+str(i+1) + '" name="answer'+str(i+1)
            inp += '"><option selected="selected" value="">-----</option>'
            ans = Question.objects.get(pk=ques[i].id).get_answers()
            for q in range(len(ans)):
                inp += '<option value="'+str(ans[q].pk)+'">'+ans[q].answer+'</option>'
            inp += '</select>'
        elif ques[i].type == Question.QUESTION_TYPE_TEXT:
            inp = '<input id="id_answer' + str(i+1) + '" name="answer' + str(i+1) + '" type="text">'
        html += '<p class="text-center">' + ques[i].question + '</p>' + '<p class="text-center">' + inp + '</p>'
    return html


def generate_forms(ques):
    form = []
    for i in ques:
        if i['type'] == Question.QUESTION_TYPE_MULTIPLE:
            form.append(MultipleChoiceForm)
        elif i['type'] == Question.QUESTION_TYPE_SINGLE:
            form.append(SingleChoiceForm)
        elif i.type == Question.QUESTION_TYPE_TEXT:
            form.append(TextfieldForm)
    return form


def generate_safe_forms(ques, request):
    form = TextfieldForm(request.POST)
    v = 1
    for i in ques:
        help_text = i.description if i.description else None
        if i.type == Question.QUESTION_TYPE_MULTIPLE:
            form.fields['answer'+str(v)] = forms.ModelMultipleChoiceField(widget=widgets.SelectMultiple(attrs={'style': 'width:100%;text-align:center', }), queryset=i.get_answers(), label=ques[v-1].question, required=i.required, help_text=help_text)
        elif i.type == Question.QUESTION_TYPE_SINGLE:
            form.fields['answer'+str(v)] = forms.ModelChoiceField(widget=widgets.Select(attrs={'style': 'width:100%;text-align:center', }), queryset=i.get_answers(), required=i.required, label=ques[v-1].question, help_text=help_text, empty_label=None)
        elif i.type == Question.QUESTION_TYPE_TEXT:
            form.fields['answer'+str(v)] = forms.CharField(widget=widgets.TextInput(attrs={'style': 'width:100%;text-align:center', }),max_length=255, label=ques[v-1].question, required=i.required, help_text=help_text)
        elif i.type == Question.QUESTION_TYPE_SCALA:
            form.fields['answer'+str(v)] = forms.IntegerField(widget=widgets.NumberInput(attrs={'type': 'range', 'oninput': 'answer'+str(v)+'Out.value=answer'+str(v)+'.value', 'max': str(i.number_range_end), 'step': '1', 'value': str(int(i.number_range_end/2))}), required=i.required, label=ques[v-1].question, help_text=help_text)
        v += 1
    return form
