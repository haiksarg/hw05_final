from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        'текст_поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.text[:settings.STR_LIMIT]


class Group(models.Model):
    title = models.CharField(
        'название_группы',
        max_length=200,
        help_text='Введите название группы',
    )
    slug = models.SlugField(
        'ссылка',
        blank=True,
        null=False,
        unique=True,
    )
    description = models.TextField(
        'описание группы',
        help_text='Введите описание группы'
    )

    class Meta:
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    text = models.TextField(
        'текст_поста',
        help_text='Текст нового комментария',
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name_plural = 'коментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='который подписывается',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='на которого подписываются',
    )

    class Meta:
        verbose_name_plural = 'подписки'
