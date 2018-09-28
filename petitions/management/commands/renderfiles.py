from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string
from os import listdir
from os.path import isfile, join

import os
import json

class Command(BaseCommand):
    petitions_dir = os.path.join(settings.BASE_DIR, "petitions/static")
    profile_dir = os.path.join(settings.BASE_DIR, "profile/static")

    def handle(self, *args, **options):

        petition_file_names = [f for f in listdir(self.petitions_dir) if isfile(join(self.petitions_dir, f))]
        profile_file_names = [f for f in listdir(self.profile_dir) if isfile(join(self.profile_dir, f))]
        
        colors = settings.CUSTOMIZATION["colors"]
        data_object = {
            'colors': colors,
            'customization': json.dumps(settings.CUSTOMIZATION),
            'default_title': settings.CUSTOMIZATION['default_title'],
            'default_body': settings.CUSTOMIZATION['default_body']
        }

        # Grab all fil e names in petitions/static
        for file in petition_file_names:
            path = self.petitions_dir + "/" + file
            template = render_to_string(path, data_object)
            static_dir = ""
            
            # Check file extension
            ext = file.split(".")[1]
            if ext == "css":
                static_dir = os.path.join(settings.BASE_DIR, 'static/css/'+file)
            elif ext == "js":
                static_dir = os.path.join(settings.BASE_DIR, 'static/js/'+file)

            with open(static_dir, 'w+') as f:
                f.write(template)

        for file in profile_file_names:
            path = self.profile_dir + "/" + file
            template = render_to_string(path, data_object)
            static_dir = ""
            
            # Check file extension
            ext = file.split(".")[1]
            if ext == "css":
                static_dir = os.path.join(settings.BASE_DIR, 'static/css/'+file)
            elif ext == "js":
                static_dir = os.path.join(settings.BASE_DIR, 'static/js/'+file)

            with open(static_dir, 'w+') as f:
                f.write(template)
        
        print("Rendered the following " + str(petition_file_names) + str(profile_file_names))
        
