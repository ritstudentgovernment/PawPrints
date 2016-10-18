from django.test import TestCase, Client
from django.contrib.auth.models import User
from petitions.models import Petition, Tag
from datetime import datetime, timedelta
from .views import petition_sign

class PetitionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superUser = User.objects.create_user(username='txu1267', email='txu1267', is_staff=True)
        self.superUser.set_password('test')
        self.superUser.save()
        self.user = User.objects.create_user(username='axu7254', email='axu7254')
        self.tag = Tag(name='Test')
        self.tag.save()
        self.petition = Petition(title='Test petition',  
                description='This is a test petition', 
                author=self.user,
                created_at=datetime.utcnow(),
                published=True,
                expires=datetime.utcnow()+timedelta(days=30)
                )
        self.petition.save()

    def test_sign_petition(self):
        self.client.force_login(self.superUser)
        response = self.client.post('/petition/sign/'+str(self.petition.id), {})
        pet = Petition.objects.get(pk=self.petition.id)
        self.assertEqual(pet.signatures, 1)

