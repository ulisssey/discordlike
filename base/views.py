from django.core.checks import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *


@csrf_exempt
def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, "User doesn't exist.")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    context = {'page': page}
    return render(request, 'base/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
    return render(request, 'base/login.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    topics = Topic.objects.all()[0:3]
    context = {'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    rooms = Room.objects.get(id=pk)
    participants = rooms.participants.all()
    room_messages = rooms.message_set.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=rooms,
            body=request.POST.get('body')
        )
        rooms.participants.add(request.user)
        return redirect('room', pk=rooms.id)
    
    context = {'rooms': rooms, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userprofile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages,
               'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login/')
def createroom(request):
    form = RoomForm
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login/')
def updateroom(request, pk):
    rooms = Room.objects.get(id=pk)
    form = RoomForm(instance=rooms)
    topics = Topic.objects.all()

    if request.user != rooms.host:
        return redirect('home')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        rooms.name = request.POST.get('name')
        rooms.topic = topic
        rooms.description = request.POST.get('description')
        rooms.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'rooms': rooms}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login/')
def deleteroom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='/login/')
def deletemessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return redirect('home')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateuser(request):
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=request.user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicspage(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activitypage(request):
    messages = Message.objects.all()
    return render(request, 'base/activity.html', {'messages': messages})