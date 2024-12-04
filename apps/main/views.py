from django.shortcuts import render, redirect
from apps.bot.models import bots
from django.db.models import Count
from apps.board.models import postdb
from django.utils import timezone


# Create your views here.
def index(request):
    botlist = bots.objects.all().order_by('-id')[:20]

    context = postdb.objects.all().order_by('-date').annotate(comment_count=Count('comments'))[:39]
    today = timezone.now().date()

    return render(request, 'main/main.html', {'botlist':botlist, 'context':context, 'today': today})