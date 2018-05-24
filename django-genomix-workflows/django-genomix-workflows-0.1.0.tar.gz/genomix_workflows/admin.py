# -*- coding: utf-8
from django.contrib import admin
from django.utils.safestring import mark_safe
import json

from . import models


class TaskAdmin(admin.ModelAdmin):
    model = models.Task
    list_display = ('id', 'label', 'get_all_previous')
    filter_horizontal = ('previous',)


class WorkflowAdmin(admin.ModelAdmin):
    model = models.Workflow
    list_display = ('id', 'label', 'version')
    filter_horizontal = ('task',)


class WorkflowInstanceAdmin(admin.ModelAdmin):
    model = models.WorkflowInstance
    list_display = ('id', 'workflow', 'content_type', 'object_id',)
    readonly_fields = (
        '_graph_diagram',
        '_graph_json',
        '_combined_graph',
        '_combined_graph_json'
    )

    class Media:
        css = {
            "all": ('css/graph.css',)
        }
        js = ('https://d3js.org/d3.v5.js',
              'js/dagre-d3.js',
              'js/graph.js',)

    def _graph_diagram(self, obj):
        json_string = "'" + json.dumps(obj.get_graph()) + "'"
        result = u'<svg class="graph1" width="700" height="400" data=%s ></svg>' % json_string
        return mark_safe(result)

    def _graph_json(self, obj):
        json_string = obj.get_graph()
        result = u'<pre>%s</pre>' % json_string
        return mark_safe(result)

    def _combined_graph(self, obj):
        json_string = "'" + json.dumps(self.model.objects.get_combined_graph(obj)) + "'"
        result = u'<svg class="graph2" width="700" height="500" data=%s ></svg>' % json_string
        return mark_safe(result)

    def _combined_graph_json(self, obj):
        json_string = self.model.objects.get_combined_graph(obj)
        result = u'<pre>%s</pre>' % json_string
        return mark_safe(result)


class TaskInstanceAdmin(admin.ModelAdmin):
    model = models.TaskInstance
    list_display = ('id', 'task', 'workflow_instance', 'status', '_previous',)
    readonly_fields = ('_previous', '_combined_previous')

    def _previous(self, obj):
        return "\n".join([str(ti) for ti in obj.previous_task_instances()])

    def _combined_previous(self, obj):
        return "\n".join([str(ti) for ti in self.model.objects.combined_previous_task_instances(obj)])


class ReferenceAdmin(admin.ModelAdmin):
    model = models.Reference
    list_display = ('id', 'content_type', 'object_id', 'workflow')


admin.site.register(models.Reference, ReferenceAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskInstance, TaskInstanceAdmin)
admin.site.register(models.Workflow, WorkflowAdmin)
admin.site.register(models.WorkflowInstance, WorkflowInstanceAdmin)
