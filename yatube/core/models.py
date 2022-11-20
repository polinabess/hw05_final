from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
        help_text='Отметьте дату публикации поста'
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True
