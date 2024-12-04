from django import forms
from .models import bots, Botcategory

class botForm(forms.ModelForm):
    class Meta:
        model = bots
        fields = ['botImg', 'name', 'category', 'descript', 'firstMessage', 'comment' ]  # 입력받을 필드 지정
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '봇 이름을 입력하세요'}),
            'descript': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '봇 설명을 입력하세요', 'rows': 3}),
            'firstMessage': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '첫 메시지를 입력하세요', 'rows': 2}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '다른사람들에게 봇을 소개하는 문장을 입력하세요', 'rows': 2}),
            'botImg': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    category = forms.ModelChoiceField(
        queryset=Botcategory.objects.all(),  # Category 모델의 모든 객체를 가져옴
        empty_label="카테고리 선택",  # 기본 선택지
        widget=forms.Select(attrs={'class': 'category-select'}),
        required=True
    )