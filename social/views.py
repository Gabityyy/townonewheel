from social.models import Relationship
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import generic
from django.views import View
from django.contrib import auth
from django.contrib.auth.models import User

from social.services import UserService, SignupDto, LoginDto, UpdateDto, RelationShipDto, RelationShipService, CatRelationShipService, CatRelationShipDto

from crud.models import Cat, CatImage
from config.settings import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_S3_REGION_NAME,AWS_STORAGE_BUCKET_NAME
from boto3.session import Session
from datetime import datetime

class IndexTemplateView(generic.ListView):
    model = Cat
    context_object_name = 'cats'
    queryset = Cat.objects.all()
    template_name = 'index.html'
    object_list = Cat.objects.all()

    def get(self, request):
        context = super().get_context_data()
        context['test'] = 'test'
        return render(request, 'index.html', context)

    def post(self, request):
        context = super().get_context_data()
        context['position'] = request.POST['position']
        return render(request, 'index.html', context)

class SignupView(View):
    def get(self, request, *args, **kwargs) :
        return render(request, 'signup.html')

    def post(self, request, *args, **kwargs):
        signup_dto = self._build_signup_dto(request.POST)
        result = UserService.signup(signup_dto)
        
        if(result['error']['state']):
            context = {'error': result['error']}
            return render(request, 'signup.html', context)
        auth.login(request, result['user'])
        return redirect('index')
        
    @staticmethod
    def _build_signup_dto(post_data) :
        return SignupDto(
            userid=post_data['userid'],
            profile_img_url=post_data['image'],
            password=post_data['password'],
            password_check=post_data['password_check'],
            introduction=post_data['introduction'],
            name=post_data['name'],
            email=post_data['email'],
        )

class LoginView(View) :
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        login_dto = self._build_login_dto(request.POST)
        result = UserService.login(login_dto)
        if (result['error']['state']):
            context = {'error' : result['error']}
            return render(request, 'login.html', context)
        auth.login(request, result['user'])
        return redirect('index')

    @staticmethod
    def _build_login_dto(post_data):
        return LoginDto(
            userid=post_data['userid'],
            password=post_data['password']
        )

def logout(request) :
    auth.logout(request)
    return redirect('index')

class EditView(View) :
    def get(self, request, *args, **kwargs):
        context = {'user' : UserService.find_by(kwargs['pk'])}
        return render(request, 'edit.html', context)

    def post(self, request, *args, **kwargs):
        update_dto = self._build_update_dto(request.POST)
        result = UserService.update(update_dto)
        if (result['error']['state']):
            context = {'error':result['error']}
            return render(request, 'edit.html', context)
        return redirect('index')
    
    def _build_update_dto(self, post_data):
        return UpdateDto(
            name=post_data['name'],
            email=post_data['email'],
            introduction=post_data['introduction'],
            pk=self.kwargs['pk']
        )
    
def delete(request, user_pk):
    user = User.objects.filter(pk=user_pk)

    user.update(is_active=False)
    auth.logout(request)

    return redirect('index')

class RelationShipView(View):
    def post(self, request, *args, **kwargs):
        relationship_dto = self._build_relationship_dto(request)
        result = RelationShipService.toggle(relationship_dto)

        return redirect('social:detail', kwargs['pk'])
    
    def _build_relationship_dto(self, request):
        return RelationShipDto(
            user_pk=self.kwargs['pk'],
            requester=request.user
        )

class DetailView(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'detail.html'

class CatRelationShipView(View):
    def post(self, request, *args, **kwargs):
        catrelationship_dto = self._build_catrelationship_dto(request)
        result = CatRelationShipService.toggle(catrelationship_dto)

        return redirect('crud:cat_detail', kwargs['pk'])
    
    def _build_catrelationship_dto(self, request):
        return CatRelationShipDto(
            cat_pk=self.kwargs['pk'],
            requester=request.user
        )

class FavoriteView(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'favorite.html'

