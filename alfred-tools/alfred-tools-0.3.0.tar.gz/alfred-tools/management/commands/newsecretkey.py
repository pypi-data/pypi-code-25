from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import random

class Command(BaseCommand):
    help = 'Hi this is one Secret Key Generator'

    def handle(self, *args, **options):
        key_id = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])    	
        print("The new key is (copy/paste in your settings file):\n " + key_id)

    	
    	



    
    
    