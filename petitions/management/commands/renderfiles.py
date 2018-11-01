"""
Renders css/js files to use config data in config.yml

Peter Zujko 
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string
from os import listdir
from os.path import isfile, join

import os
import json
import base64


class Command(BaseCommand):
    petitions_dir = os.path.join(settings.BASE_DIR, "petitions/static")
    profile_dir = os.path.join(settings.BASE_DIR, "profile/static")

    def handle(self, *args, **options):
        CONFIG = settings.CONFIG
        social = []
        # Set icons to base64
        for icon in CONFIG['social']['social_links']:
            data = icon
            file_loc = settings.BASE_DIR+icon['imgURL']
            ext = file_loc.split('.')[1]
            with open(file_loc, 'rb') as file:
                data_str = ""
                if ext == 'svg':
                    data_str = "data:image/svg+xml;utf8;base64,"
                elif ext == 'png':
                    data_str = "data:image/png;base64,"
                data['imgURL'] = data_str + \
                    base64.b64encode(file.read()).decode("utf-8")
            social.append(data)

        petition_file_names = [f for f in listdir(
            self.petitions_dir) if isfile(join(self.petitions_dir, f))]
        profile_file_names = [f for f in listdir(
            self.profile_dir) if isfile(join(self.profile_dir, f))]
        colors = settings.CONFIG["ui"]["colors"]
        data_object = {
            'name': CONFIG['name'],
            'colors': colors,
            'header_title': CONFIG['text']['header_title'],
            'images': CONFIG['ui']['slideshow_images'],
            'social': social,
            'default_title': CONFIG['petitions']['default_title'],
            'default_body': CONFIG['petitions']['default_body'],
            'org': CONFIG['organization']
        }

        # Grab all file names in petitions/static
        for file in petition_file_names:
            path = self.petitions_dir + "/" + file
            template = render_to_string(path, data_object)
            static_dir = ""

            # Check file extension
            ext = file.split(".")[1]
            if ext == "css":
                static_dir = os.path.join(
                    settings.BASE_DIR, 'static/css/'+file)
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
                static_dir = os.path.join(
                    settings.BASE_DIR, 'static/css/'+file)
            elif ext == "js":
                static_dir = os.path.join(settings.BASE_DIR, 'static/js/'+file)

            with open(static_dir, 'w+') as f:
                f.write(template)

        print("Rendered the following " +
              str(petition_file_names) + str(profile_file_names))
