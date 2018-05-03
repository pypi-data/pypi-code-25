
from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    group = models.IntegerField(blank=True, null=True)
    chinese_name = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    emp_no = models.CharField(max_length=50, blank=True, null=True)
    domain_account = models.CharField(max_length=50, blank=True, null=True)
    ticket = models.CharField(max_length=50, blank=True, null=True)
    level = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=500, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User,related_name='create_user')
    last_change_datetime = models.DateTimeField(auto_now=True)
    last_change_user = models.ForeignKey(User,related_name='last_change_user')
    # user_id = models.CharField(max_length=50, blank=True, null=True)


    def __unicode__(self):
        return self.user.username
