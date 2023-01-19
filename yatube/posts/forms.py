from django import forms

from .models import Post, Comment, Group


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст',
                  'group': 'Выберите группу',
                  'image': 'Добавьте файл'}
        help_texts = {'text': 'Любую абракадабру',
                      'group': 'Из уже существующих',
                      'image': 'Фоточку например'}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Введите текст', }
        help_texts = {'text': 'Любую абракадабру', }


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')
        labels = {'title': 'Hазвание группы',
                  'slug': 'Cсылка группы',
                  'description': 'Oписание группы'}
        help_texts = {'title': 'Введите название группы',
                      'slug': 'Введите ссылкy группы',
                      'description': 'Введите описание группы'}
