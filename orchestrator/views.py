from django.shortcuts import redirect, render
from .models import TestRequest
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import login as authlogin
from .forms import RequestForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as authlogin
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from .utils import FileHandler, Paginator
from django.views.generic.edit import FormView
from django.urls import reverse
from threading import Thread
from itertools import tee
from django.core.files.uploadedfile import InMemoryUploadedFile


def override_close(obj):
    """
    This function overrides the original close of the InMemoryFileObjects
    so that they're not accessible among different threads.
    The close function is deligated to a new method called new_close that
    later should be called to close the files explicitly.
    """
    def the_close(self):
        super(self).close()
    obj.new_close = obj.close
    obj.close = lambda self: None
    return obj

class BaseRedirect(View):
    def get(self, request):
        return redirect(reverse('home', kwargs={'page':1}))

class Home(View):
    """
    The very home page.
    """
    def get(self, request, page=1):
        request_count = TestRequest.objects.count()
        if request_count:
            test_list = Paginator(TestRequest.objects.all().order_by('-request_date').iterator(),
                                  range_frame=settings.RANGE_FRAME,
                                  rows_number=settings.ROW_NUMBER,)
            is_other_page = test_list.has_other_pages()
            the_page = test_list[page]
        else:
            is_other_page = test_list = the_page = None

        if self.request.user.is_authenticated:

            form = RequestForm(self.request.GET)
            return render(self.request,
                          'orchestrator/index.html',
                          {'test_requests': test_list,
                           'page': the_page,
                           'form': form,
                           'is_other_pages': is_other_page,
                           'request_count':request_count,
                           'base':'home'})
        else:
            return render(self.request,
                          'orchestrator/index.html',
                          {'test_requests': test_list,
                           'page': the_page,
                           'is_other_pages': is_other_page,
                           'request_count': request_count,
                           'base':'home'})

    def post(self, request, page=1):
        form = RequestForm(self.request.POST, self.request.FILES)
        files = self.request.FILES.getlist('file')
        files = [override_close(i) for i in files]
        model = TestRequest()
        errors = ''
        if form.is_valid():

            itf = form.cleaned_data['interface']
            env = form.cleaned_data['environment']
            # file = request.FILES['file']
            
            # Run file handler
            file_handler = FileHandler(username=request.user.username,
                                       files=files,
                                       model=model,
                                       environment=env,
                                       interface=itf)

            model.add(interface=itf,
                      environment=env,
                      user=self.request.user,
                      file_names=[f.name for f in files])

            # start file handlers in another thread
            thread = Thread(target = file_handler.run)
            thread.start()

            # pass uploaded files to the respective file handler

            # add the request to database
        
        else:
            errors = form.errors

        test_list = Paginator(TestRequest.objects.all().order_by('-request_date').iterator(),
                              range_frame=settings.RANGE_FRAME,
                              rows_number=settings.ROW_NUMBER,)
        request_count = TestRequest.objects.count()
        return render(self.request,
                      'orchestrator/index.html',
                      {'test_requests': test_list,
                       'form': form,
                       'page': test_list[1],
                       'errors': errors,
                       'request_count': request_count,
                       'is_other_pages':test_list.has_other_pages(),
                       'base':'home'})


class RecordStatus(View):
    def get(self, request, record_id):
        result = TestRequest.objects.get(id=record_id)
        failures = [f.split('\\n') for f in result.failures]

        warning = None
        if request.user.username != result.user.username:
            warning = """Sorry you're not authorized to see the result of\
            this test request """
        return render(self.request,
                    'orchestrator/record_status.html',
                    {'failures': failures,
                    'description': result.description,
                    'errors': result.errors,
                    'warning': warning})

def login(request):
    error = ''
    test_list = TestRequest.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        error = "An unhandeled error occurred! please contant Kasra that's his fault! ;))"
        try:
            user = authenticate(request, username=username, password=password)
        except KeyError:
            error = 'Fill in all fields!'
        else:
            if user is not None:
                # user is registered
                authlogin(request, user)
                return redirect(reverse('home', kwargs={'page':1}))
            else:
                error = "Invalid username and/or password!"
    return render(request,
                  'registration/login.html',
                  {'form': AuthenticationForm(),
                   'error': error,
                   'test_requests': test_list})

def signup_view(request):
    if request.method == 'POST':
        data = request.POST
        form = UserCreationForm(data)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            authlogin(request, new_user)
            return redirect(reverse('home', kwargs={'page':1}))
        else:
            return render(request,
                  'registration/signup.html',
                  {'form': form})
    return render(request,
                  'registration/signup.html',
                  {'form': UserCreationForm()})


class SpecificRequests(View):
    """Show a list all requests with a specific status"""
    
    def get(self, request, request_type, page=1):
        test_list = Paginator(TestRequest.objects.filter(state=request_type).order_by('-request_date').iterator(),
                              range_frame=settings.RANGE_FRAME,
                              rows_number=settings.ROW_NUMBER,)
        request_count = TestRequest.objects.count()
        
        return render(self.request,
                      'orchestrator/index.html',
                      {'test_requests': test_list,
                       'page': test_list[page],
                       'base':'filtered/{}'.format(request_type),
                       'request_count': request_count,
                       'is_other_pages':test_list.has_other_pages()})
