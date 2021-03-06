from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django_countries.fields import CountryField
import django_filters
from django.http import request
from django.utils import timezone
from django.utils.safestring import mark_safe
from markupsafe import text_type
from .user_ip import get_user_ip

GENDER = (
    ('Мужской', 'Мужской'),
    ('Женский', 'Женский'),
    ('Не определён', 'Не определён')
)

CLAIM_PRIORITY = (
    ('Низкая', 'Низкая'),
    ('Средняя', 'Средняя'),
    ('Высокая', 'Высокая')
)

CLAIM_STATUS = (
    ('В обработке', 'В обработке'),
    ('Принятая', 'Принятая'),
    ('Отклонённая', 'Отклонённая'),
    ('Окончательно отклонённая', 'Окончательно отклонённая')
)

CLAIM_THEME = (
    ('Не определена', 'Не определена'),
    ('Гражданские дела', 'Гражданские дела'),
    ('Уголовные дела', 'Уголовные дела'),
    ('Бизнес', 'Бизнес')
)


class MyUser(AbstractUser):
    photo = models.ImageField(verbose_name='Фотография', upload_to='images/', default='/images/bydefault/unnamed.png')
    # в default пока указана строка, нужно прописывать в save, чтобы взял файл и преобразовал в строку
    # or default, or null=True, blank=True
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic_name = models.CharField(max_length=100, verbose_name='Отчество', null=True, blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    gender = models.CharField(choices=GENDER, max_length=7, default='Не определён', verbose_name='Пол')
    email = models.EmailField(max_length=40, help_text='Введите e-mail в формате "myname@mymail.com"')
    form_of_address = models.CharField(max_length=20, null=True, blank=True)
    birthday = models.DateField(verbose_name='Дата рождения', default=datetime.now() - timedelta(days=10957.5))
    country = CountryField(verbose_name='Страна проживания', blank_label='Выберите страну проживания')
    region = models.CharField(max_length=100, verbose_name='Область / регион', null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name='Город (населённый пункт)', null=True, blank=True)
    postal_code = models.CharField(max_length=15, verbose_name='Почтовый индекс', null=True, blank=True)
    address = models.CharField(max_length=100, verbose_name='Адрес', null=True, blank=True)
    phone_number1 = models.CharField(max_length=20, verbose_name='Основной номер телефона', null=True, blank=True)
    phone_number2 = models.CharField(max_length=20, verbose_name='Дополнительный номер телефона', null=True, blank=True,
                                     help_text="Введите номер в международном формате '+380xxxxxxxxx'")
    scype = models.CharField(max_length=30, verbose_name='Scype', null=True, blank=True)
    telegram = models.CharField(max_length=30, verbose_name='Telegram', null=True, blank=True)
    viber = models.CharField(max_length=30, verbose_name='Viber', null=True, blank=True)
    whatsapp = models.CharField(max_length=3, verbose_name='WhatsApp', null=True, blank=True)
    user_site = models.URLField(verbose_name='Введите ссылку на свой сайт', null=True, blank=True)
    additional = models.TextField(max_length=1000, verbose_name='Дополнительные сведения', null=True, blank=True)
    user_file = models.FileField(verbose_name='Загрузить файл', upload_to='files/', null=True, blank=True)

    def __str__(self):
        return "Пользователь {}".format(self.username)

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.pk)])

    class Meta:
        ordering = ['id', 'last_name']


class Claim(models.Model):
    theme = models.CharField(choices=CLAIM_THEME, default="Не определена", max_length=250, verbose_name="Тема")
    priority = models.CharField(choices=CLAIM_PRIORITY, default="Средняя", max_length=10,
                                verbose_name="Степень важности")
    text = models.TextField(max_length=40000, verbose_name='Текст заявки (не более 40 000 знаков)',
                            null=True, blank=True)
    client = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING, verbose_name="Пользователь")
    application_date = models.DateTimeField(verbose_name="Дата и время подачи заявки", auto_now_add=True)
    application_update = models.DateTimeField(verbose_name="Дата и время обновления заявки", auto_now=True)
    status = models.CharField(choices=CLAIM_STATUS, default="В обработке", max_length=25, verbose_name="Статус")
    first_rejected = models.BooleanField(default=False, verbose_name="Отклонена")
    first_rejected_comment = models.TextField(max_length=10000, verbose_name='Причина отклонения',
                                              default="В данный момент все специалисты заняты")
    restore_request = models.BooleanField(default=False, verbose_name="Запрос на восстановление")
    restore_request_text = models.TextField(max_length=10000, verbose_name='Причина восстановления',
                                            default="Просьба восстановить заявку")
    finally_rejected = models.BooleanField(default=False, verbose_name="Окончательно отклонена")
    finally_rejected_comment = models.TextField(max_length=10000, verbose_name='Причина окончательного отклонения',
                                                default="Заявку невозможно обработать")
    restored = models.BooleanField(default=False, verbose_name="Восстановлена")
    documents = models.FileField(verbose_name='Загрузить документы (один файл)', upload_to='files/', null=True,
                                 blank=True)

    class Meta:
        ordering = ['-priority', '-application_date', 'client']


class ClientClaimFilter(django_filters.FilterSet):
    class Meta:
        model = Claim
        fields = ['theme', 'priority', 'restored', 'status']


class Comment(models.Model):
    to_claim = models.ForeignKey(Claim, on_delete=models.CASCADE, verbose_name="Обрабатываемая заявка")
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Ваш комментарий")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Комментарий создан")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Комментарий обновлен")

    class Meta:
        ordering = ['-date_updated', 'to_claim']
