# -*- coding: utf-8 -*-
from django.db.models import Q, Manager
import json
import networkx as nx
from networkx import json_graph

from . import models


class WorkflowManager(Manager):

    def current_state(self, **kwargs):
        queryset = self
        objects = kwargs["objects"]
        filter = Q()
        for object in objects:
            object_id = object['object_id']
            content_type = object['content_type']
            filter |= Q(object_id=object_id) & Q(content_type__model=content_type)

        queryset = queryset.filter(filter)

        return queryset

    def get_combined_graph(self, obj):
        G = nx.DiGraph()
        wf_instances = []
        combined_task_instances = models.TaskInstance.objects

        if obj.parent is None:
            wf_instances.extend(obj.get_all_children())
        else:
            wf_instances.extend(obj.parent.get_all_children())

        combined_task_instances = combined_task_instances.filter(workflow_instance__in=wf_instances)

        for task_instance in combined_task_instances:

            previous_tasks = task_instance.task.previous.all()

            for previous in previous_tasks:
                # find previous in task instances if exists
                # if (task_instance.task.id == previous.id):
                if combined_task_instances.filter(task__id=previous.id):
                    previous_task_instances = combined_task_instances.filter(task__id=previous.id)
                    # also check to make sure the two instance workflows are directly related
                    if task_instance.workflow_instance.parent is not None:
                        previous_task_instances = previous_task_instances.filter(
                            Q(workflow_instance=task_instance.workflow_instance.parent) |
                            Q(workflow_instance=task_instance.workflow_instance)
                        )
                    for pti in previous_task_instances:
                        # add the previous instance and its edge to graph
                        G.add_node(task_instance.id,
                                   status=task_instance.get_status_display(),
                                   label=task_instance.task.label,
                                   group=task_instance.workflow_instance.id,
                                   )
                        G.add_node(pti.id,
                                   status=pti.get_status_display(),
                                   label=pti.task.label,
                                   group=pti.workflow_instance.id,
                                   )
                        G.add_edge(pti.id, task_instance.id)

        graph = json.dumps(json_graph.node_link_data(G), indent=2)
        return graph


class TaskManager(Manager):

    def combined_previous_task_instances(self, obj):
        previous_instances = []
        wf_instances = []
        combined_task_instances = models.TaskInstance.objects

        if obj.workflow_instance.parent is None:
            wf_instances.extend(obj.workflow_instance.get_all_children())
        else:
            wf_instances.extend(obj.workflow_instance.parent.get_all_children())

        combined_task_instances = combined_task_instances.filter(workflow_instance__in=wf_instances)

        for previous in obj.task.previous.all():
            # check if a task instance exists in the wf instance
            if combined_task_instances.filter(task__id=previous.id):
                pi = combined_task_instances.filter(task__id=previous.id).first()
                # add the previous instance to the list
                previous_instances.append(pi)
        return previous_instances
