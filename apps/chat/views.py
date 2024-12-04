from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
import json, os, re, logging
from dotenv import load_dotenv

from openai import OpenAI
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold, SafetySetting

from .models import Chats, Message
from apps.bot.models import bots

logger = logging.getLogger('django')
load_dotenv()

client = OpenAI(api_key = os.getenv('api_key'))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sinuous-studio-442919-c4-c01909279fde.json'

def make_prompt(bot_data, chat_id, bot_category):
    if bot_category.name == '인물' or bot_category.name == '캐릭터':
        with open('static/prompt.txt', 'r', encoding='utf-8') as file:
            prompt = file.read()
    
            bot_data_position = prompt.find('(AI Character)')

            if bot_data_position != -1:
                prompt = prompt[:bot_data_position + len('(AI Character)')] + '\n' + bot_data + prompt[bot_data_position + len('(AI Character)'):]
            
            chatsession_position = prompt.find('#<Chat Start>')

            messages = Message.objects.filter(chat_id=chat_id).order_by('-id')[:5]
            chatsession = ""
            for message in messages[::-1]:
                chatsession += f"<user>: {message.user}\n"
                chatsession += f"<char>: {message.assistant}\n"
            
            if bot_data_position != -1:
                prompt = prompt[:chatsession_position + len('#<Chat Start>')] + '\n' + chatsession + prompt[chatsession_position + len('#<Chat Start>'):]
        return prompt
    
    else:
        with open('static/prompt2.txt', 'r', encoding='utf-8') as file:
            prompt = file.read()
    
            bot_data_position = prompt.find('(AI Character)')

            if bot_data_position != -1:
                prompt = prompt[:bot_data_position + len('(AI Character)')] + '\n' + bot_data + prompt[bot_data_position + len('(AI Character)'):]
            
            chatsession_position = prompt.find('#<Chat Start>')

            messages = Message.objects.filter(chat_id=chat_id).order_by('-id')[:5]
            chatsession = ""
            for message in messages[::-1]:
                chatsession += f"<user>: {message.user}\n"
                chatsession += f"<char>: {message.assistant}\n"
            
            if bot_data_position != -1:
                prompt = prompt[:chatsession_position + len('#<Chat Start>')] + '\n' + chatsession + prompt[chatsession_position + len('#<Chat Start>'):]
        
            return prompt

#openAi API 요청 함수 (반환값은 ai_response(str))
def openai_api_response(
        selected_model,
        custom_prompt,
        bot,
        user_input,
        temperature,
        top_p,
        frequency_penalty,
        presence_penalty,
        chat_id = None,
):  
    prompt = make_prompt(bot.descript, chat_id, bot.category)
    
    try:
        response = client.chat.completions.create(
            model = selected_model,
            messages=[
                {"role": "system", "content": (custom_prompt if custom_prompt != "" else prompt)},
                {"role": "user", "content": user_input },
            ],
            temperature = float(temperature),
            top_p = float(top_p),
            frequency_penalty = float(frequency_penalty),
            presence_penalty = float(presence_penalty),
        )

        # max_tokens = 5000, 나중에 추가
        
        print("Response model:", response.model)  # 응답 내용을 로그로 확인
        print("Response completion_tokens:", response.usage.completion_tokens)
        print("Response prompt_tokens:", response.usage.prompt_tokens)
        print("Response total_tokens:", response.usage.total_tokens)

        response = response.json()
        data = json.loads(response)
        ai_response = data['choices'][0]['message']['content']
        ai_response = ai_response.replace("<char>", bot.name).replace("<user>", "User")

    except Exception as e:
        ai_response = f"Error: {str(e)}"

    return ai_response

def gemini_api_response(
        selected_model,
        custom_prompt,
        bot,
        user_input,
        temperature,
        top_p,
        frequency_penalty,
        presence_penalty,
        project_id = os.getenv('project_id'),
        chat_id = None,
):  
    # "max_output_tokens": 4096, 나중에 추가
    generation_config = {
        "temperature": float(temperature),
        "top_p": float(top_p),
        "frequency_penalty": float(frequency_penalty),
        "presence_penalty": float(presence_penalty)
    }
    
    # Safety config
    safety_config = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_NONE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_NONE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_NONE,
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_NONE,
        ),
    ]

    prompt = make_prompt(bot.descript, chat_id, bot.category)

    system_instruction = (custom_prompt if custom_prompt != "" else prompt)
    vertexai.init(project=project_id, location="asia-northeast3")
    model = GenerativeModel(selected_model, system_instruction=system_instruction)
    user_message = user_input
    
    try:
        response = model.generate_content(user_message, generation_config=generation_config, safety_settings=safety_config)

        start_idx = str(response).find("usage_metadata")
        print(str(response)[start_idx:])
        logger.info(f"{str(response)[start_idx:]}")

        return response.text.replace("<char>", bot.name).replace("<user>", "User")

    except Exception as e:
        response = f"Error: {str(e)}"

        return response

#입력된 모델이 어느 회사것인지 검사하는 함수
def get_provider_for_model(model_name):
    # 모델 리스트 정의
    LlmModels = [
        ["gpt-3.5-turbo", "gpt-4o-mini"],  # OpenAI 모델 목록
        ["gemini-1.5-flash-001", "gemini-1.5-pro-001"]  # Google Gemini 모델 목록
    ]

    if model_name in LlmModels[0]:
        return "openai"

    elif model_name in LlmModels[1]:
        return "google"

# Create your views here.
def chat(request, user_id=None, bot_id=None, chat_id=None):
    if request.method == "POST":
        data = json.loads(request.body)
        bot = bots.objects.get(id=bot_id)

        api_params = {
            "selected_model": data.get("selected_model"),
            "custom_prompt": data.get("custom_prompt", ""),
            "bot": bot,
            "user_input": data.get("user_input", ""),
            "temperature": data.get("temperature", 1),
            "top_p": data.get("top_p", 1),
            "frequency_penalty": data.get("frequency_penalty", 0),
            "presence_penalty": data.get("presence_penalty", 0),
        }

        print(api_params)
        logger.info(f"{api_params}")

        if get_provider_for_model(api_params["selected_model"]) == "openai":
            # ai_response = openai_api_response(**api_params, chat_id=chat_id)
            ai_response = "현재 비용상의 문제로 잠시 OpenAi GPT 모델은 사용중지 상태입니다. 자세한 사항은 관리자에게 연락하세요."
        else:
            ai_response = gemini_api_response(**api_params, chat_id=chat_id)

        #반환값 테스트
        print(ai_response)
        logger.info(f"{ai_response}")

        #db에 메세지 저장
        chat = get_object_or_404(Chats, id=chat_id, user=request.user)
        message = Message.objects.create(chat=chat, user=api_params["user_input"], assistant=ai_response)

        return JsonResponse({"ai_response": ai_response})
    
    else:
        # 새로운 Chat 생성
        if chat_id is None:  # 기존 채팅이 없는 경우 새로 생성
            chat = Chats.objects.create(user=request.user, title="New chat", bot_id=bot_id)

            #퍼스트 메시지 저장 
            chat = get_object_or_404(Chats, id=chat.id, user=request.user)
            bot = bots.objects.get(id=bot_id)
            message = Message.objects.create(chat_id=chat.id, user='', assistant=bot.firstMessage)

            chat_id = chat.id
            bot_id = bot_id
            return HttpResponseRedirect(f'/chat/{user_id}/{bot_id}/{chat_id}')
        else:  # 기존 채팅 가져오기
            chat = get_object_or_404(Chats, id=chat_id, user=request.user)
    
            # 기존 메시지 가져오기 (불러온 값 html에 추가 해야함!!!)
            messages = chat.messages.all().order_by("timestamp")
            bot = bots.objects.get(id=bot_id)
            return render(request, 'chat/chat.html', {"chat_id": chat.id, "messages": messages, "bot": bot, 'current_chat_id': int(chat_id) })
        
def delete_chat(request):
    if request.method == "POST":
        chat_id = request.POST.get("chat_id")
        current_chat_id = request.POST.get("current_chat_id")  # 현재 보고 있는 채팅 ID 가져오기

        # 채팅 삭제 로직
        Chats.objects.filter(id=chat_id).delete()
        messages.success(request, "채팅이 삭제되었습니다.")
        
        referer = request.META.get('HTTP_REFERER', '/')
        if str(chat_id) == str(current_chat_id):  # 삭제한 채팅이 현재 채팅일 때
            return redirect('/')  # '/'로 리다이렉트
        else:  # 삭제한 채팅이 현재 채팅이 아닐 때
            return HttpResponseRedirect(referer)  # 이전 페이지로 리다이렉트