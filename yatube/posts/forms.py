from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Тут напишите ваш тест поста',
            'group': 'Выберете группу',
            'image': 'Загрузите картинку'
        }


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Ваш комментарий тут'
        }
