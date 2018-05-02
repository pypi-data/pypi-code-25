from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class BaseAuthProfile(models.Model):

    # User object associated with this profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    # User access token
    token = models.TextField()
    # User refresh token (optional)
    refresh_token = models.TextField(null=True)

    @staticmethod
    def register_or_update_user(token, refresh_token, **data):
        raise NotImplementedError


class GoogleAuthProfile(BaseAuthProfile):
    # Google's resource ID for this user
    resource_id = models.CharField(max_length=100, unique=True)
    # This user's email
    email = models.EmailField()

    @staticmethod
    def register_or_update_user(token, refresh_token, **data):
        if not GoogleAuthProfile.objects.filter(resource_id=data['resource_id']).exists():
            auth = GoogleAuthProfile(
                email=data['email'],
                resource_id=data['resource_id'],
                token=token,
                refresh_token=refresh_token
            )
        else:
            auth = GoogleAuthProfile.objects.get(resource_id=data['resource_id'])

        user = User.objects.get_or_create(
            username=auth.email,
            email=auth.email,
            first_name=data['first_name'],
            last_name=data['last_name']
        )[0]
        auth.user = user
        auth.save()
        return auth

    def __str__(self):
        return "GoogleAuthProfile de " + self.user.email
