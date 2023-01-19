from django.db import models

from core.models import CreatedModel, User


class Post(CreatedModel):
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta(CreatedModel.Meta):
        verbose_name_plural = 'посты'
        default_related_name = 'posts'


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
        help_text='Введите ссылкy группы',
    )
    description = models.TextField(
        'описание группы',
        help_text='Введите описание группы'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )

    class Meta:
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост'
    )

    class Meta(CreatedModel.Meta):
        verbose_name_plural = 'коментарии'
        default_related_name = 'comments'


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
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_relationships',
                fields=["user", "author"],),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F("author")),),
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f'подписан на {self.author.username}')
