from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.author = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.urls_and_names = (
            ('posts:index', None, '/'),
            ('posts:group_list',
             (f'{self.group.slug}',),
             f'/group/{self.group.slug}/'),
            ('posts:profile',
             (f'{self.author.username}',),
             f'/profile/{self.author.username}/'),
            ('posts:post_detail',
             (f'{self.post.pk}',),
             f'/posts/{self.post.pk}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit',
             (f'{self.post.pk}',),
             f'/posts/{self.post.pk}/edit/'),
            ('posts:add_comment',
             (f'{self.post.pk}',),
             f'/posts/{self.post.pk}/comment/'),
            ('posts:follow_index', None, '/follow/'),
            ('posts:profile_follow',
             (f'{self.user.username}',),
             f'/profile/{self.user.username}/follow/'),
            ('posts:profile_unfollow',
             (f'{self.user.username}',),
             f'/profile/{self.user.username}/unfollow/'),
        )
        cache.clear()

    def test_urls_equal_names(self):
        """Проверка соответствия urls и names."""
        for reverse_name, argum, url in self.urls_and_names:
            with self.subTest(reverse_name=reverse_name, url=url, argum=argum):
                self.assertEqual(
                    reverse(
                        reverse_name,
                        args=argum
                    ),
                    url)

    def test_author_client(self):
        """Проверка доступности страниц для автора."""
        for reverse_name, arguments, _ in self.urls_and_names:
            with self.subTest(reverse_name=reverse_name, arguments=arguments):
                response = self.authorized_author.get(
                    reverse(
                        reverse_name,
                        args=arguments),
                    follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_client(self):
        """Проверка доступности страниц для авторизованных пользователей."""
        follows = ['posts:profile_follow', 'posts:profile_unfollow']
        for reverse_name, arguments, _ in self.urls_and_names:
            with self.subTest(reverse_name=reverse_name, arguments=arguments):
                if reverse_name in follows:
                    response = self.authorized_client.get(
                        reverse(
                            reverse_name,
                            args=(self.author.username,)),
                        follow=True)
                else:
                    response = self.authorized_client.get(
                        reverse(
                            reverse_name,
                            args=arguments),
                        follow=True)
                if reverse_name == 'posts:post_edit':
                    self.assertRedirects(
                        response,
                        reverse(
                            'posts:post_detail',
                            args=(f'{self.post.pk}',)))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_client(self):
        """Проверка доступности страниц для неавторизованных пользователей."""
        redirects = ['posts:post_create', 'posts:post_edit']
        for reverse_name, arguments, _ in self.urls_and_names:
            with self.subTest(reverse_name=reverse_name, arguments=arguments):
                response = self.client.get(
                    reverse(
                        reverse_name,
                        args=arguments),
                    follow=True)
                if reverse_name in redirects:
                    self.assertRedirects(
                        response,
                        reverse('users:login') + '?next=' + reverse(
                            reverse_name,
                            args=arguments))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверка страниц на использование правильных шаблонов."""
        templates_and_names = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list',
             (f'{self.group.slug}',),
             'posts/group_list.html'),
            ('posts:profile',
             (f'{self.author.username}',),
             'posts/profile.html'),
            ('posts:post_detail',
             (f'{self.post.pk}',),
             'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/post_create.html'),
            ('posts:post_edit',
             (f'{self.post.pk}',),
             'posts/post_create.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
        )
        for rev_name, argum, temp in templates_and_names:
            with self.subTest(rev_name=rev_name, argum=argum, temp=temp):
                response = self.authorized_author.get(
                    reverse(
                        rev_name,
                        args=argum),
                    follow=True)
                self.assertTemplateUsed(response, temp)

    def test_error(self):
        """Проверка 404."""
        response = self.client.get('/unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/eror.html')
