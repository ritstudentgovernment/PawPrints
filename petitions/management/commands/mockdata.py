import traceback
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from profile.models import Profile, Notifications
from petitions.models import Tag, Petition
import random
from mimesis import Personal, Text

class Command(BaseCommand):
    help = "Generates fake data for PawPrints"
    tag_names = ['Technology', 'Academics', 'Parking & Transportation', 'Other', 'Dining', 'Sustainability', 'Facilities', 'Housing', 'Public Safety', 'Campus Life', 'Governance', 'Clubs & Organizations', 'Deaf Advocacy']

    def add_arguments(self, parser):
        parser.add_argument('-wipe', dest='flag_exists', action='store_true', help='Wipes all data in the database but does not generate anything after')
        parser.add_argument('--users', dest='users', help='The number of users to generate (default: 250 users)', type=int, default=250)
        parser.add_argument('--petitions', dest='petitions', help='The number of petitions to generate (default: 150 petitions)', type=int, default=150)
        parser.add_argument('--expired', dest='expired', help='The number of expired petitions to generate (default: none)', type=int, default=0)
        parser.add_argument('--unpublished', dest='unpub', help='The number of unpublished petitions to generate (default: none)', type=int, default=0)
        parser.add_argument('--removed', dest='removed', help='The number of removed petitions to generate (default: none)', type=int, default=0)
        parser.add_argument('--review', dest='review', help='The number of petitions that need review to generate (default: none)', type=int, default=0)

        parser.add_argument('--email', dest='email', nargs='+', help='List of email address to be added for a user profile')
        parser.add_argument('--signatures', dest='sigs', nargs='+', help='List of integers which represent signatures', type=int)
        parser.add_argument('--responded', dest='resp', help='The number of petitions which have a response (NOTE: This currently does not generate response objects. It just sets the has_response bool to True) (default: 0)', type=int, default=0)

    def handle(self, *args, **options):
        wipe = options['flag_exists']
        num_petitions = options['petitions']
        num_users = options['users'] 
        emails = options['email']
        num_sigs = options['sigs']
        expired = options['expired']
        unpub = options['unpub']
        removed = options['removed']
        review = options['review']
        resp = options['resp']
        
        if wipe:
            Petition.objects.all().delete()
            User.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully wiped data'))
            return


        # Generate django user objects
        django_users = self.generate_users(num_users, emails)
        # Set generated profile data
        self.set_profile_data(django_users)

        # Generate Tag objects
        Tag.objects.all().delete()
        tags = self.generate_tags()

        # Generate petition objects
        petitions = self.generate_petitions(django_users, expired, unpub, removed, review, num_sigs, num_petitions, resp)

        # Set petitiond values
        self.set_petition_relations(tags, petitions, django_users)

    def set_petition_relations(self, tags, petitions, django_users):
        self.stdout.write('Setting Petition relations')
        try:
            with transaction.atomic():
                for petition in petitions:
                    num_tags = random.randint(1,4)
                    random.shuffle(tags)
                    tags_to_add = tags[0:num_tags]
                    sigs = petition.signatures


                    petition.tags.add(*tags_to_add)
                    petition.save()
                    django_users.remove(petition.author) # Remove so they dont sign twice
                    random.shuffle(django_users)
                    users_to_sign_petition = django_users[1:sigs]
                    for user in users_to_sign_petition:
                        user.profile.petitions_signed.add(petition)
                        user.save()
                    
                    django_users.append(petition.author)
                    auth = petition.author
                    auth.profile.petitions_created.add(petition)
                    auth.profile.petitions_signed.add(petition)
                    auth.save()

            self.stdout.write(self.style.SUCCESS('Successfully set Petition relations'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to set relations %s' % e))
            print(traceback.format_exc())
        
    def generate_petitions(self, users, expired, unpub, removed, review, sigs, num_petitions, resp):
        petitionlst = []
        self.stdout.write('Generating Petition objects')
        text = Text('en')
        try:
            with transaction.atomic():
                for x in range(0, num_petitions):
                    # Generate/Grab data
                    num_sentences = random.randint(1,6)
                    title = text.sentence()[0:80]
                    description = text.text(num_sentences)
                    author = random.choice(users)
                    if sigs:
                        signatures = sigs.pop()
                    else:
                        signatures = random.randint(1, len(users))
                    created_at = timezone.now() - timedelta(days=random.randint(0, 10))
                    status = 1
                    expires = created_at + timedelta(days=30)                    
                    last_signed = created_at + timedelta(days=random.randint(0,10))
                    petition = Petition()
                    if expired > 0:
                        created_at = timezone.now() - timedelta(days=31)
                        expires = created_at + timedelta(days=30) 
                        last_signed = created_at + timedelta(days=random.randint(1, 30))
                        expired -= 1
                    elif unpub > 0:
                        status = 0
                        unpub -= 1
                    elif removed > 0:
                        status = 2
                        removed -= 1
                    elif review > 0:
                        status =  3
                        review -= 1

                    petition.author = author
                    petition.title = title
                    petition.description = description
                    petition.signatures = signatures
                    petition.created_at = created_at
                    petition.status = status
                    petition.expires = expires
                    petition.last_signed = last_signed
                    if resp > 0:
                        petition.has_response = True
                        resp -= 1

                    petition.save()
                    petitionlst.append(petition)
            self.stdout.write(self.style.SUCCESS('Successfully created %s Petition objects' % num_petitions))
            return petitionlst
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to generate %s Petition objects\n %s' % (len(users), e)))
            print(traceback.format_exc())
            return None
     

    def generate_tags(self):
        taglst = []
        self.stdout.write('Generating Tag objects')
        try:
            with transaction.atomic():
                for tag in self.tag_names:
                    tag_obj = Tag(name=tag)
                    tag_obj.save()
                    taglst.append(tag_obj)

            self.stdout.write(self.style.SUCCESS('Successfully created Tag objects'))
            return taglst
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to create Tag objects\n %s' % e))
            return None


    def set_profile_data(self, users):
        self.stdout.write('Updating profile data')
        personlst = [Personal('cs'), Personal('en')]
        try:
            with transaction.atomic():
                for user in users:
                    person = random.choice(personlst)
                    fullname = person.full_name()
                    name = fullname.split()
                    first = name[0]
                    last = name[1]
                    user.first_name = first
                    user.last_name = last
                    user.profile.full_name = fullname
                    user.profile.display_name = fullname[0:3].upper()
                    user.profile.has_access = 1
                    user.save()

            self.stdout.write(self.style.SUCCESS('Successfully updated %s profiles' % len(users)))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to update %s Profile objects\n %s' % (len(users), e)))
        
    def generate_users(self, num_users, emails):
        self.stdout.write('Generating django User objects')
        personlst = [Personal('cs'), Personal('en')]
        userlst = []
        try:
            with transaction.atomic():
                for x in range(0, num_users):
                    person = random.choice(personlst)
                    if emails:
                        email_addr = emails.pop()
                    else:
                        email_addr = person.email(['doesnotexist.c'])

                    user = User(email=email_addr,is_active=True, username=person.username())
                    user.set_unusable_password()
                    user.save()
                    userlst.append(user)
            self.stdout.write(self.style.SUCCESS('Successfully generated %s users' % num_users))
            return userlst
        except Exception as e:
            self.stdout.write(self.style.ERROR('Failed to generate %s users\n %s' % (num_users, e)))
            return None

