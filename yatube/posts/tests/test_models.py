from django.conf import settings as stgs
from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
            author=cls.user,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 123',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.__str__(), self.post.text[:stgs.STR_LIMIT])
        self.assertEqual(self.group.__str__(), self.group.title)

    def test_post_verbose_name(self):
        """verbose_names модели post совпадает с ожидаемым."""
        field_verbose = {
            'text': 'текст',
            'pub_date': 'Дата создания',
            'author': 'автор',
            'group': 'группа',
        }
        for field, verbose1 in field_verbose.items():
            with self.subTest(field=field, verbose1=verbose1):
                verbose2 = self.post._meta.get_field(field).verbose_name
                self.assertEqual(verbose1, verbose2)

    def test_group_verbose_name(self):
        """verbose_names модели group совпадает с ожидаемым."""
        field_verbose = {
            'title': 'название_группы',
            'slug': 'ссылка',
        }
        for field, verbose1 in field_verbose.items():
            with self.subTest(field=field, verbose1=verbose1):
                verbose2 = self.group._meta.get_field(field).verbose_name
                self.assertEqual(verbose1, verbose2)

    def test_post_help_text(self):
        """help_texts модели post совпадает с ожидаемым."""
        field_help_text = {
            'text': 'Введите текст',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, help_text1 in field_help_text.items():
            with self.subTest(field=field, help_text1=help_text1):
                help_text2 = self.post._meta.get_field(field).help_text
                self.assertEqual(help_text1, help_text2)

    def test_group_help_text(self):
        """help_texts модели group совпадает с ожидаемым."""
        field_help_text = {
            'title': 'Введите название группы',
            'description': 'Введите описание группы',
        }
        for field, help_text1 in field_help_text.items():
            with self.subTest(field=field, help_text1=help_text1):
                help_text2 = self.group._meta.get_field(field).help_text
                self.assertEqual(help_text1, help_text2)
