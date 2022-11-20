from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_of_posts',
        verbose_name='Автор',
        help_text='Укажите автора поста'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts_of_group',
        verbose_name='Группа',
        help_text='Выберете группу поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        # выводим текст поста
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Прокомментированный пост',
        help_text='Добавленные комментарии к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Добавте автора комментария'
    )
    text = models.TextField(max_length=400, verbose_name='Текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Cсылка на объект пользователя, который подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Ссылка на объект пользователя, на которого подписываются'
    )
