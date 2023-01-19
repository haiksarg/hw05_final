import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Post, Group, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='testfollower')
        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
            author=cls.user,
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.pages = (
            ('?page=1', settings.UPDATETS_LIMIT),
            ('?page=2', settings.UPDATETS_LIMIT_TWO)
        )
        cache.clear()

    def test_context_form(self):
        """Проверка контекста view-функций, содержащих в нем ПостФорму"""
        view_context_form_reverses = (
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.pk,)),
        )
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.models.ModelChoiceField),
            ('image', forms.fields.ImageField)
        )
        for view_reverse, arguments in view_context_form_reverses:
            with self.subTest(view_name=view_reverse, arguments=arguments):
                response = self.authorized_client.get(
                    reverse(
                        view_reverse,
                        args=arguments),
                    follow=True)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context.get('form'), PostForm)
                for field, field_class in form_fields:
                    with self.subTest(field=field, field_class=field_class):
                        self.assertIsInstance(
                            response.context.get('form').fields.get(field),
                            field_class
                        )

    def contexter(self, response, pages=False):
        """Функция, распределяющая проверки по содержанию контекста"""
        fields = ('text', 'author', 'pub_date', 'group', 'image')
        if pages:
            post = response.context.get('post')
        else:
            post = response.context.get('page_obj')[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    getattr(self.post, field))

    def test_context_index(self):
        """Проверка контекста view-функции index"""
        response = self.authorized_client.get(reverse(
            'posts:index'))
        self.contexter(response)

    def test_context_group(self):
        """Проверка контекста view-функции group_posts"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=(self.group.slug,)))
        self.contexter(response)
        self.assertIsInstance(response.context['group'], Group)

    def test_context_profile(self):
        """Проверка контекста view-функции profile"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            args=(self.user.username,)))
        self.contexter(response)
        self.assertIsInstance(response.context['author'], User)

    def test_other_group(self):
        """Проверка того, что посты не попали не в ту группу"""
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='testslugtwo',
            author=self.user,
            description='Тестовое описание 2')
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=(group_2.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=(self.group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_context_post_detail(self):
        """Проверка контекста view-функции post_detail"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.pk,)))
        self.contexter(response, True)

    def test_len_paginator(self):
        """Проверка пагинации"""
        posts = []
        for number in range(settings.TEST_PAGINATOR):
            posts.append(Post(
                author=self.user,
                text=f'Post {number}',
                group=self.group))
        Post.objects.bulk_create(posts, batch_size=13)
        Follow.objects.create(
            user=self.follower,
            author=self.user)
        pag_names = (
            ('posts:index', None),
            ('posts:group_list',
             (self.group.slug,)),
            ('posts:profile',
             (self.user.username,)),
            ('posts:follow_index', None),)
        for reverse_name, arguments in pag_names:
            with self.subTest(reverse_name=reverse_name, arguments=arguments):
                for page, limit in self.pages:
                    with self.subTest(page=page, limit=limit):
                        response = self.authorized_follower.get(reverse(
                            reverse_name,
                            args=arguments) + page)
                        context = response.context.get('page_obj')
                        self.assertEqual(len(context), limit)

    def test_cache_index(self):
        """Проверка кеширования данных главной страницы"""
        response1 = self.authorized_client.get(reverse(
            'posts:index'))
        Post.objects.all().delete()
        response2 = self.authorized_client.get(reverse(
            'posts:index'))
        self.assertEqual(
            response1.content,
            response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse(
            'posts:index'))
        self.assertNotEqual(
            response1.content,
            response3.content)

    def test_following(self):
        """Проверка работы подписок"""
        count1 = Follow.objects.count()
        self.authorized_follower.get(
            reverse(
                'posts:profile_follow',
                args=(self.user.username,)),
            follow=True)
        count2 = Follow.objects.count()
        self.assertEqual(count1 + 1, count2)
        follow = Follow.objects.get(
            user=self.follower,
            author=self.user)
        self.assertEqual(follow.user, self.follower)
        self.assertEqual(follow.author, self.user)

    def test_unfollowing(self):
        """Проверка работы отписок"""
        Follow.objects.create(
            user=self.follower,
            author=self.user)
        count1 = Follow.objects.count()
        self.authorized_follower.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.user.username,)),
            follow=True)
        count2 = Follow.objects.count()
        self.assertEqual(count1 - 1, count2)

    def test_displaying_a_post_on_the_follow_index_page(self):
        """Проверка отображения поста на странице follow_index"""
        Follow.objects.create(
            user=self.follower,
            author=self.user)
        response1 = self.authorized_follower.get(reverse('posts:follow_index'))
        context1 = response1.context.get('page_obj')
        self.assertEqual(len(context1), 1)
        Follow.objects.get(
            user=self.follower,
            author=self.user).delete()
        response2 = self.authorized_follower.get(reverse('posts:follow_index'))
        context2 = response2.context.get('page_obj')
        self.assertEqual(len(context2), 0)

    def test_follow_yourself(self):
        """Проверка, что нельзя подписаться на самого себя"""
        count1 = Follow.objects.count()
        self.authorized_follower.get(
            reverse(
                'posts:profile_follow',
                args=(self.follower.username,)),
            follow=True)
        count2 = Follow.objects.count()
        self.assertEqual(count1, count2)

    def test_duble_follow(self):
        Follow.objects.create(
            user=self.follower,
            author=self.user)
        count1 = Follow.objects.count()
        self.authorized_follower.get(
            reverse(
                'posts:profile_follow',
                args=(self.user.username,)),
            follow=True)
        count2 = Follow.objects.count()
        self.assertEqual(count1, count2)

    def test_post_delete(self):
        """Проверка удаления постов"""
        count1 = Post.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:post_delete',
                args=(self.post.pk,)))
        count2 = Post.objects.count()
        self.assertEqual(count1 - 1, count2)
