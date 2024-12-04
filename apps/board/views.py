from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count
from .forms import writeForm
from .models import postdb, Comment, Postlike, Category

from bs4 import BeautifulSoup
def extract_image_sources(html_content):
    """HTML 콘텐츠에서 모든 <img> 태그의 src 속성을 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    img_sources = [img.get('src') for img in img_tags if img.get('src')]
    return img_sources

# Create your views here.
def index(request, category_id=None):

    page = request.GET.get('page', '1')
    sort_by = request.GET.get('sort_by', 'latest')
    
    # 정렬 기준에 따른 queryset 정렬
    if category_id == 1:
        if sort_by == 'latest':
            context = postdb.objects.all().order_by('-date').annotate(comment_count=Count('comments'))
        elif sort_by == 'likes':
            context = postdb.objects.all().order_by('-likes').annotate(comment_count=Count('comments'))
        elif sort_by == 'views':
            context = postdb.objects.all().order_by('-counting').annotate(comment_count=Count('comments'))
        else:
            context = postdb.objects.all().order_by('-date').annotate(comment_count=Count('comments'))  # 기본값
    else:
        if sort_by == 'latest':
            context = postdb.objects.filter(category_id=category_id).order_by('-date').annotate(comment_count=Count('comments'))
        elif sort_by == 'likes':
            context = postdb.objects.filter(category_id=category_id).order_by('-likes').annotate(comment_count=Count('comments'))
        elif sort_by == 'views':
            context = postdb.objects.filter(category_id=category_id).order_by('-counting').annotate(comment_count=Count('comments'))
        else:
            context = postdb.objects.filter(category_id=category_id).order_by('-date').annotate(comment_count=Count('comments'))  # 기본값
    
    paginator = Paginator(context, 30)
    page_obj = paginator.get_page(page)

    today = timezone.now().date()
    categories = Category.objects.all()

    return render(request, 'board/list.html', {
        'context': page_obj,
        'today': today,
        'categories': categories,
        'category_id': category_id,
        'sort_by': sort_by
    })

def read(request, id):
    if request.method == 'POST':
        parent_comment_id = request.POST.get('parent_comment_id')
        print(parent_comment_id)

        if parent_comment_id and parent_comment_id.isdigit():
            parent_comment = Comment.objects.get(id=parent_comment_id)
        else:
            parent_comment = None

        Comment.objects.create(
            post = postdb.objects.get(id=id),
            parent_comment = parent_comment,
            comment_body = request.POST['comment'],
            user = request.user)
        
        return redirect(request.path)
    else:
        context = postdb.objects.get(id=id)
        comments = context.comments.filter(parent_comment__isnull=True)
        context.counting += 1
        context.save(update_fields=['counting'])

        #댓글 개수
        comment_len = context.comments.count()
        
        return render(request, 'board/read.html', {'context':context, 'comments':comments, 'comment_len':comment_len})

@csrf_exempt
def write(request):
    if request.method == 'GET':
        form = writeForm()
        return render(request, 'board/write.html' , {'form':form})
    elif request.method == 'POST':
        form = writeForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # commit=False로 저장 연기
            post.user = request.user        # 현재 로그인한 사용자 추가
            post.save() 

            #이미지 Url 따오기
            imageUrl = extract_image_sources(post.body)
            if len(imageUrl) != 0:
                p = postdb.objects.get(id=post.id)
                p.imgUrl = imageUrl[0]
                p.save()

            url = '/board/read/' + str(post.id)
            return redirect(url)
        else:
            return render(request, 'board/write.html', {'form': form})
    # elif request.method == 'POST':
    #     p = postdb.objects.create(title=request.POST['title'], body=request.POST['body'])
    #     url = '/read/' + str(p.id)
    #     p.save()

    #     return redirect(url)

@csrf_exempt
def delete(request):
    if request.method == 'POST':
        id = request.POST['id']
        postdb.objects.get(id=id).delete()

    return redirect('/board/')

@csrf_exempt
def update(request, id):
    if request.method == 'GET':
        context = postdb.objects.get(id=id)
        form = writeForm(instance=context)
        return render(request, 'board/update.html', {'form':form})
    elif request.method == 'POST':
        p = postdb.objects.get(id=id)
        p.title = request.POST['title']
        p.body = request.POST['body']
        p.save()

        return redirect(f'/board/read/{id}')
    
def like_post(request, post_id):
    if not request.user.is_authenticated:  # 로그인하지 않은 사용자는 추천 불가
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=403)
    
    post = get_object_or_404(postdb, id=post_id)
    
    # 사용자가 이미 추천했는지 확인
    if Postlike.objects.filter(user=request.user, post=post).exists():
        return JsonResponse({'error': '이미 추천했습니다.', 'likes': post.likes}, status=400)
    
    # 추천 기록 추가
    Postlike.objects.create(user=request.user, post=post)
    post.likes += 1
    post.save(update_fields=['likes'])
    
    return JsonResponse({'likes': post.likes})