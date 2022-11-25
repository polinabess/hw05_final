from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post

User = get_user_model()


class CacheIndexTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='AuthorPost')
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Тестовый пост'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self) -> None:
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author_post)
        cache.clear()

    def test_cache_index(self):
        """Записи страницы index кэшируются успешно."""
        response = self.authorized_author.get(reverse('posts:index'))
        cache_with_post = response.content
        Post.objects.get(id=self.post.id).delete()
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual(cache_with_post, response.content, "Кэш не работает.")
        cache.clear()
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertNotEqual(
            cache_with_post,
            response.content,
            "Очистка кэша не сработала."
        )
