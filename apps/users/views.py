from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import joinForm

# from .models import users

# Create your views here.
def join(request):
    if request.method == 'GET':
        form = joinForm()
        return render(request, 'users/join.html', {'form':form})
    elif request.method == 'POST':
        form = joinForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'users/join.html', {'form':form})