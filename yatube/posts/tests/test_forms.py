import tempfile
import shutil

from ..forms import PostForm
from ..models import Post, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# при отправке валидной формы со страницы создания поста
# reverse('posts:create_post') создаётся новая запись в базе данных;
# при отправке валидной формы со страницы редактирования поста
# reverse('posts:post_edit', args=('post_id',)) происходит изменение поста с
# post_id в базе данных.


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
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
            group=cls.group
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

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

    def test_create_page_create_new_post(self):
        """Валидная форма создает запись."""
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif'
            ).exists()
        )

    def test_create_page_edit_post(self):
        """Валидная форма редактирует запись."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый пост',
            'group': self.group.id
        }
        response = self.authorized_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            form_data['text']
        )

    def test_post_commented_by_authorized_user(self):
        """Комментировать посты может
        только авторизованный пользователь"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий'
        }
        guest_response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        authorized_response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(guest_response.status_code, HTTPStatus.OK)
        self.assertEqual(authorized_response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.assertRedirects(
            authorized_response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=self.post.id,
                author=self.user.id
            ).exists()
        )
