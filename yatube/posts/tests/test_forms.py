import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Group, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='testslug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_post_create(self):
        """Проверка корректного создания поста"""
        Post.objects.all().delete()
        count1 = Post.objects.all().count()
        fields = {'text': 'testtext',
                  'group': self.group.pk,
                  'image': self.uploaded
                  }
        self.authorized_client.post(
            reverse('posts:post_create'),
            fields,
            follow=True)
        count2 = Post.objects.all().count()
        self.assertEqual(count1 + 1, count2)
        new_post = Post.objects.first()
        self.assertEqual(new_post.text, fields['text'])
        self.assertEqual(new_post.group.pk, fields['group'])
        self.assertEqual(new_post.image, 'posts/small.gif')
        self.assertEqual(new_post.author, self.user)

    def test_post_edit(self):
        """Проверка корректного редактирования поста"""
        self.assertEqual(Post.objects.all().count(), 1)
        fields = {'text': 'newtext',
                  'group': self.group_2.pk,
                  'image': self.uploaded
                  }
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=(self.post.pk,)),
            fields,
            follow=True)
        post = Post.objects.first()
        self.assertEqual(post.text, fields['text'])
        self.assertEqual(post.group.pk, fields['group'])
        self.assertEqual(post.author, self.post.author)
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                args=(self.group.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 0)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_unauthorized_user_cannot_create_post(self):
        Post.objects.all().delete()
        count1 = Post.objects.all().count()
        fields = {'text': 'testtext', 'group': self.group.pk}
        self.client.post(
            reverse('posts:post_create'),
            fields,
            follow=True)
        count2 = Post.objects.all().count()
        self.assertEqual(count1, count2)

    def test_unauthorized_user_cannot_create_comment(self):
        Comment.objects.filter(post=self.post).delete()
        count1 = Comment.objects.filter(post=self.post).count()
        fields = {'text': 'testtext'}
        self.client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,)),
            fields,
            follow=True)
        count2 = Comment.objects.filter(post=self.post).count()
        self.assertEqual(count1, count2)

    def test_authorized_user_can_create_comment(self):
        Comment.objects.filter(post=self.post).delete()
        count1 = Comment.objects.filter(post=self.post).count()
        fields = {'text': 'testtext'}
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.pk,)),
            fields,
            follow=True)
        count2 = Comment.objects.filter(post=self.post).count()
        self.assertEqual(count1 + 1, count2)
