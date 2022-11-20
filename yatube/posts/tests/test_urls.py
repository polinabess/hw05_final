# posts/tests/test_urls.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='AuthorPost')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Тестовый пост',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='SimpleUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author_post)

    def test_unexisting_url_is_404(self):
        """Страница не существует."""
        template = 'unexisting_page/'
        response = self.guest_client.get(template)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        urls_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        for urls in urls_names:
            response = self.guest_client.get(urls)
            with self.subTest(adress=urls):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        for urls, templates in urls_templates_names.items():
            with self.subTest(adress=urls):
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, templates)

    def test_create_url_redirect_anonymous(self):
        """Страница перенаправят анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(reverse(
            'posts:post_create'), follow=True
        )
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_edit_url_redirect_user(self):
        """Страница редактированиия поста автора
        недоступна для обычного пользователя."""
        post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_url_correct_templates(self):
        """Страница редактирования использует
        соответствующий шаблон и доступна автору."""
        post_id = self.post.id
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')
