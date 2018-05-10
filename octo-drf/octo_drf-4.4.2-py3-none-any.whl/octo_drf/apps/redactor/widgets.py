import os

from django import forms
from django.utils.safestring import mark_safe


class Redactor(forms.Textarea):
    buttons = '''\'html', 'formatting', 'bold', 'italic', 'deleted',
    'unorderedlist', 'orderedlist', 'outdent', 'indent', 'image', 'video',
    'file', 'table', 'link', 'alignment', 'horizontalrule', 'fullscreen\''''
    redactor_type = 'standart'

    class Media:
        css = {
            'all': ('redactor/redactor.css', ),
        }
        js = (
            'jquery-2.2.4.min.js',
            'redactor/plugins/add_buttons.js',
            'redactor/plugins/video.js',
            'redactor/plugins/textdirection.js',
            'redactor/plugins/fullscreen.js',
            'redactor/plugins/table.js',
            'redactor/redactor.min.js',
            'redactor/ru.js',
        )

    def __init__(self, attrs=None):
        self.attrs = attrs
        if attrs:
            self.attrs.update(attrs)
        super(Redactor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.redactor_type == 'inline':
            attrs.update({'class': 'redactor_inline'})
        rendered = super(Redactor, self).render(name, value, attrs)
        parameters = '''
            plugins: ['video', 'fullscreen', 'table', ],
            minHeight: 200,
            maxHeight: 300,
            focus: false,
            buttonSource: true,
            buttons: [%s],
            imageUpload: '/__upload_img/',
            fileUpload: '/__upload_file/',
            lang: 'ru',
            replaceTags: [
                ['strike', 'del'],
                ['h1', 'p']
            ],
            replaceDivs: false,
            toolbarFixed: false,
            formatting: ['p', 'blockquote', 'h2', 'h3', 'h4', 'h5'],
            formattingAdd: [
                {
                    tag: 'p',
                    title: 'Стилизованный абзац',
                    class: 'marked_piece'
                }
            ]

        ''' % self.buttons
        if self.redactor_type == 'inline':
            if u'__prefix__' not in name:
                rendered = rendered + mark_safe(u'''
                <script type="text/javascript">
                    $(function() {
                            $('#id_%s').redactor({
                                %s
                            });
                        });
                </script>''' % (name, parameters))
            else:
                rendered = rendered + mark_safe(u'''
                <script type="text/javascript">
                    $(function(){
                            $('body').off('click', '.add-row a').on("click", '.add-row a', function(){
                                var parent = $(this).parents('.inline-group');
                                parent.find('.redactor_inline').eq(-2).redactor({
                                    %s
                                });
                            });
                        });
                </script>''' % parameters)
        else:
            rendered = rendered + mark_safe(u'''<script type="text/javascript">
            $(document).ready(
                function()
                {
                    $('#id_%s').redactor({
                        %s
                    });
                }
            );
            </script>''' % (name, parameters))
        return rendered


class RedactorInline(Redactor):
    redactor_type = 'inline'
