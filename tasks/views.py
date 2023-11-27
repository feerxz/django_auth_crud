from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #el módulo htt contiene varias clases y funciones relacionadas con el manejo del protocolo HTTP. Se utilizan más HttpResponse y HttpRequest

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #UserCreationForm: FORMULARIO que ya me da django para hacer autenticación (registrar un usuario), y AuthenticationForm para comprobar si el usuario existe

from django.contrib.auth import login, logout, authenticate # LOGIN:Crea la cookie para guardar datos del usuario en el navegador, como recordar la autenticación, etc. LOGOUT: elimina la cookie (quita la sesión). AUTHENTICATE: sirve para autenticar a un usuario, devuelve una instancia del usuario autenticado, de lo contrario devuelve NONE

from django.db import IntegrityError #Importo error de integridad para manejarlo despúes en el bloque try-except

from django.contrib.auth.models import User #Clase que me da django para registrar usuarios en la base de datos

from .forms import CreateTaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required #Sirve para proteger las rutas


# Create your views here.

def home(request): #REQUEST es un parámetro que ofrece Django para obtener información del cliente que ha visitado la página, siempre hay que ponerlo.
    return render(request, 'home.html') #RENDER espera como primer parámetro "request" y despúes el nombre del archivo que quiero enviar.

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']: # 'password1' y 'password2' salen del atributo "name" que tienen los 'inputs' en el html (ver tools for developers in the browser)
            try:  # Se utiliza un bloque "try except" para manejar posibles errores que se produzcan por las validaciones propias de las configuraciones de la DB.
                user = User.objects.create_user(username= request.POST['username'], password= request.POST['password1'] ) #se crea el usuario pero aún no se guarda en la DB.
                user.save() #ahora sí se guarda en la DB.
                login(request, user)
                return redirect('tasks')
            except IntegrityError: #Atrapo el error
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Password do not match'
                })
@login_required
def tasks(request):
    tasks = Task.objects.filter(user= request.user, date_completed__isnull=True)
    return render(request, 'tasks.html', {
        'tasks': tasks,
        'show_completed': False
    })

@login_required
def show_tasks_completed(request):
    tasks = Task.objects.filter(user= request.user, date_completed__isnull=False).order_by('-date_completed') #anteponiendo un "-" al campo del argumento las ordeno en forma descendente
    return render(request, 'tasks.html', {
        'tasks': tasks,
        'show_completed': True
    })

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': CreateTaskForm
        })
    else:
        try:
            form = CreateTaskForm(request.POST)
            new_task = form.save(commit=False) #utilizo el atributo "commit=False" para que Django no me guarde inmediatamente la instancia del modelo asociado al formulario y así poder hacer modificaciones adicionales
            new_task.user = request.user #como cada modelo "Task" tiene asociado un usuario, tengo que pasarle ese argumento que viene de la sesión guardada de la cookie en el "request"
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
            'form': CreateTaskForm
        })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        #task = Task.objects.get(pk = task_id)
        task = get_object_or_404(Task, pk= task_id, user= request.user)
        form = CreateTaskForm(instance=task) #con la propiedad "instance" le paso los valores al formulario para que lo llene y cree una instancia (objeto)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task_ = get_object_or_404(Task, pk= task_id, user= request.user)
            form = CreateTaskForm(request.POST, instance= task_)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task_,
                'form': form,
                'error': 'Error updating task'
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    
@login_required
def signout(request):
    logout(request)
    return redirect('home')


def login_(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username= request.POST['username'], password= request.POST['password'])
        
        if user is None:
            return render(request, 'login.html', {
            'form': AuthenticationForm,
            'error': 'Username or password is incorrect'
        })
        else:
            login(request, user)
            return redirect('tasks')

    