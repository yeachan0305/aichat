from django import forms
from .models import postdb, Category

from django_summernote.widgets import SummernoteWidget

class writeForm(forms.ModelForm):
    class Meta:
        model = postdb
        fields = ['title', 'body', 'category']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'title',
                    'placeholder': '제목'
                }
            ),
            'body': SummernoteWidget(
                attrs={
                    'class': 'body',
                    'summernote': {'background-color': '#222222',}
                }
            ),
        }
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),  # Category 모델의 모든 객체를 가져옴
        empty_label="카테고리 선택",  # 기본 선택지
        widget=forms.Select(attrs={'class': 'category-select'}),
        required=True
    )