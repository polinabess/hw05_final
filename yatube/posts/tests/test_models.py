from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group
        str_method_text = {
            post.text[:15]: str(post),
            group.title: str(group)
        }
        for value, excepted_value in str_method_text.items():
            with self.subTest(field=value):
                self.assertEqual(
                    value, excepted_value
                )

    def test_model_has_correct_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verbose_name = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_model_has_correct_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Текст поста',
            'pub_date': 'Отметьте дату публикации поста',
            'author': 'Укажите автора поста',
            'group': 'Выберете группу поста'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
