from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from .models import bots, Botcategory
from .forms import botForm

# Create your views here.
def lists(request, category_id=None):
    page = request.GET.get('page', '1')

    if category_id:
        bot_list = bots.objects.filter(category_id=category_id).order_by('-id')
    else:
        bot_list = bots.objects.all().order_by('-id')

    paginator = Paginator(bot_list, 20)
    page_obj = paginator.get_page(page)

    categories = Botcategory.objects.all()

    return render(request, 'bot/bot_list.html', {'context':page_obj, 'categories':categories, 'category_id':category_id})

@csrf_exempt
def create(request):
    if request.method == 'POST':
        form = botForm(request.POST, request.FILES)  # 이미지 업로드를 위해 request.FILES 포함
        if form.is_valid():
            bot = form.save(commit=False)  # commit=False로 저장 연기
            bot.user = request.user        # 현재 로그인한 사용자 추가
            bot.save() 

            # 이미지 크롭 처리
            if bot.botImg:
                bot.crop_image()  # 이미지 크롭 메서드 호출

            return redirect('/')  # 저장 후 리다이렉트
    else:
        form = botForm()
    return render(request, 'bot/create_bot.html', {'form': form})