from apps.chat.models import Chats
from apps.bot.models import bots
from apps.board.models import postdb
from django.db.models import Q

# base.html에서 로그인된경우 사용자의 채팅목록 반환
def base_info(request):
    if (request.user.is_authenticated):
        chat_lists = Chats.objects.filter(user=request.user)
        bot_lists = bots.objects.all()
    else:
        chat_lists = None
        bot_lists = []
    return {
        'chat_lists': chat_lists,
        'bot_lists': bot_lists
    }

def search_context(request):
    query = request.GET.get('q', '')  # 검색어 가져오기
    bot_results = []
    post_results = []

    if query:  # 검색어가 있을 경우만 검색 실행
        bot_results = bots.objects.filter(
            Q(name__icontains=query) | Q(descript__icontains=query)
        )
        post_results = postdb.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )
    
    print(f"""
          search_query: {query},
        search_bot_results: {bot_results},
        search_post_results: {post_results}""")

    return {
        'search_query': query,
        'search_bot_results': bot_results,
        'search_post_results': post_results,
    }