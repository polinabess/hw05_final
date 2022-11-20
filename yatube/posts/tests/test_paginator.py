from django.contrib.auth import get_user_model
from django.test import TestCase
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

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно POSTS_ON_PAGE.
        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            AMOUNT_POSTS - POSTS_ON_PAGE
        )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:profile'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:profile') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            AMOUNT_POSTS - POSTS_ON_PAGE
        )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            AMOUNT_POSTS - POSTS_ON_PAGE
        )
