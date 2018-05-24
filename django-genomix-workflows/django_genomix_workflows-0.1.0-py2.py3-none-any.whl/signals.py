# -*- coding: utf-8
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.WorkflowInstance)
def workflow_instance_post_save(sender, **kwargs):
    """
    After WorkflowInstance.save is called, we look for all the related tasks in
    the workflow and make a copy of them in the TaskInstance.
    """

    instance = kwargs["instance"]
    workflow = instance.workflow
    # Create an Instance of each Task using the referenced workflow
    for task in workflow.task.all():
        models.TaskInstance.objects.create(task=task,
                                           workflow_instance=instance,
                                           status=False)
