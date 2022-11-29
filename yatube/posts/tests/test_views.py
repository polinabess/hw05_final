import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

from django import forms
from ..models import Post, Group, Follow

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.author_post = User.objects.create_user(username='AuthorPost')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.empty_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='SimpleUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author_post)

    #  Проверка шаблонов
    def test_posts_pages_uses_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        pages_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.author_post.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for page, template in pages_template_names.items():
            with self.subTest(page=page):
                response = self.authorized_author.get(page)
                self.assertTemplateUsed(response, template)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_page_shows_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_create'
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)
        self.assertTrue(response.context['page_obj'][0].image)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        slug = self.group.slug
        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': slug}
            )
        )
        self.check_context_contains_page_or_post(response.context)
        self.assertTrue(response.context['page_obj'][0].image)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile_page сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author_post.username}
            )
        )
        self.check_context_contains_page_or_post(response.context)
        self.assertIn('context', response.context)
        self.assertEqual(response.context['context'], self.post.author)
        self.assertTrue(response.context['page_obj'][0].image)

    def test_post_detail_page_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.check_context_contains_page_or_post(response.context, post=True)
        self.assertIn('context', response.context)
        self.assertEqual(response.context['context'], self.post.author)

    def test_post_not_in_group(self):
        """Пост не попадает в другую группу."""
        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.empty_group.slug}
            )
        )
        first_object = len(response.context['page_obj'])
        self.assertEqual(first_object, 0)

    def test_profile_follow(self):
        """Подписка на автора осуществляется успешно."""
        follower_cnt = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follower_cnt + 1)

    def test_profile_unfollow(self):
        """Отписка на автора осуществляется успешно."""
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author}
            )
        )
        follower_cnt = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follower_cnt - 1)
