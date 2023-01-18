from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField(
        'текст',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:settings.STR_LIMIT]
