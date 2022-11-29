from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()

AMOUNT_POSTS = 13
POSTS_ON_PAGE = 10


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='AuthorPost')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        posts_list = []
        for i in range(AMOUNT_POSTS):
            posts_list.append(
                Post(
                    author=cls.author_post,
                    text=f'Тестовый пост {i}-й',
                    group=cls.group
                )
            )
        Post.objects.bulk_create(posts_list)

    def setUp(self) -> None:
        self.unauthorized_client = Client()

    def test_pages_contain_records(self):
        """Проверка количества записей на странице."""
        pages = (
            (1, POSTS_ON_PAGE),
            (2, AMOUNT_POSTS - POSTS_ON_PAGE)
        )
        urls = (
            ('posts:index', {}),
            ('posts:profile', {'username': self.author_post.username}),
            ('posts:group_list', {'slug': self.group.slug}))
        for url, kwargs in urls:
            for page, count in pages:
                with self.subTest(url=url):
                    response = self.unauthorized_client.get(
                        reverse(url, kwargs=kwargs),
                        {'page': page}
                    )

                    self.assertEqual(
                        len(response.context.get('page_obj')),
                        count
                    )
