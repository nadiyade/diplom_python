from datetime import datetime, date, time, timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import GenericIPAddressField
from django.forms import Widget, HiddenInput
from urllib import request
from django.shortcuts import render
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from .models import GENDER, MyUser, CLAIM_STATUS, CLAIM_PRIORITY, CLAIM_THEME, Claim, Comment
from .validators import file_size, photo_size
from .user_ip import get_user_ip
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class MyForm(UserCreationForm):
    photo = forms.ImageField(label='Загрузить фото', validators=[photo_size], required=False,
                             help_text="Размер файла не должен превышать 2 MB.")
    first_name = forms.CharField(max_length=100, label='Имя*')
    patronymic_name = forms.CharField(max_length=100, label='Отчество', required=False)
    last_name = forms.CharField(max_length=100, label='Фамилия*')
    gender = forms.CharField(max_length=7, label='Пол', widget=forms.RadioSelect(choices=GENDER), required=False)
    email = forms.EmailField(max_length=40, help_text='Введите e-mail в формате "myname@mymail.com"',
                             label='E-mail*')
    form_of_address = forms.CharField(max_length=20,
                                      help_text='Предпочитаемая форма обращения, например, "Г-н/Г-жа"', required=False)
    birthday = forms.DateField(label='Дата рождения', input_formats=['%d.%m.%Y'],
                               initial=datetime.now() - timedelta(days=10957.5),
                               help_text='Введите дату рождения в формате "дд.мм.гггг"')
    country = CountryField(blank_label='Выберите страну проживания)').formfield()
    region = forms.CharField(max_length=100, label='Область / регион', required=False)
    city = forms.CharField(max_length=100, label='Город (населённый пункт)', required=False)
    postal_code = forms.CharField(max_length=15, label='Почтовый индекс', required=False)
    address = forms.CharField(max_length=100, label='Адрес', required=False)
    phone_number1 = forms.CharField(max_length=20, label='Основной номер телефона', required=False,
                                    help_text="Введите номер в международном формате '+380xxxxxxxxx'")
    phone_number2 = forms.CharField(max_length=20, label='Дополнительный номер телефона', required=False,
                                    help_text="Введите номер в международном формате '+380xxxxxxxxx'")
    scype = forms.CharField(max_length=30, label='Scype', required=False)
    telegram = forms.CharField(max_length=30, label='Telegram', required=False)
    viber = forms.CharField(max_length=30, label='Viber', required=False)
    whatsapp = forms.CharField(max_length=30, label='WhatsApp', required=False)
    user_site = forms.URLField(label='Введите ссылку на свой сайт', required=False)
    additional = forms.CharField(max_length=1000, label='Дополнительные сведения', required=False,
                                 widget=forms.Textarea(attrs={"rows": 20, "cols": 50}))
    user_file = forms.FileField(label='Загрузить файл', validators=[file_size], required=False,
                                help_text='Размер файла не должен превышать 15 MB; '
                                          'предпочтительнее в формате .pdf')
    user_IP = forms.GenericIPAddressField(disabled=True, initial="127.0.0.1")
    username = forms.CharField(max_length=40, label='Логин')

    class Meta:
        model = MyUser
        fields = ('photo', 'username', 'password1', 'password2', 'first_name', 'patronymic_name', 'last_name',
                  'gender', 'email', 'form_of_address', 'birthday', 'country', 'region', 'city', 'postal_code',
                  'address', 'phone_number1', 'phone_number2', 'scype', 'telegram', 'viber', 'whatsapp',
                  'additional', 'user_file')


class UserUpdateViewForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('photo', 'first_name', 'patronymic_name', 'last_name', 'gender', 'email', 'form_of_address',
                  'birthday', 'country', 'region', 'city', 'postal_code', 'address', 'phone_number1', 'phone_number2',
                  'scype', 'telegram', 'viber', 'whatsapp', 'additional', 'user_file')

    def __init__(self, *args, **kwargs):
        super(UserUpdateViewForm, self).__init__(*args, **kwargs)
        gender = self.fields['gender'].initial


class UserListViewForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['username', 'first_name', 'last_name']


class ClientClaimCreateViewForm(forms.ModelForm):
    theme = forms.CharField(widget=forms.Select(choices=CLAIM_THEME), label="Тема", max_length=250)
    priority = forms.CharField(label="Степень важности заявки", widget=forms.Select(choices=CLAIM_PRIORITY),
                               max_length=10)
    text = forms.CharField(max_length=40000, label='Текст заявки',
                           widget=forms.Textarea)
    application_date = forms.DateTimeField(disabled=True, label="Дата и время подачи заявки", initial=datetime.now())
    application_update = forms.DateTimeField(disabled=True, label="Дата и время обновления заявки",
                                             initial=datetime.now())
    status = forms.CharField(disabled=True, label="Статус обработки", max_length=25, initial='В обработке')
    # first_rejected = forms.BooleanField(disabled=True, label="Отклонена", initial=False)
    # finally_rejected = forms.BooleanField(disabled=True, label="Окончательно отклонена", initial=False)
    # restored = forms.BooleanField(disabled=True, label="Восстановлена", initial=False)
    documents = forms.FileField(label='Загрузить документы (один файл)', validators=[file_size], required=False,
                                help_text='Размер файла не должен превышать 15 MB; '
                                          'предпочтительнее в формате .pdf')

    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ('client', 'first_rejected', 'first_rejected_comment', 'first_rejected_comment', 'finally_rejected',
                   'finally_rejected_comment', 'restore_request', 'restore_request_text', 'restored')


class ClientClaimUpdateViewForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ('client', 'first_rejected', 'finally_rejected', 'restored')

    def __init__(self, *args, **kwargs):
        super(ClientClaimUpdateViewForm, self).__init__(*args, **kwargs)
        status = self.fields['status'].initial
        if status is not None:
            self.fields['status'].disabled = True


class ClaimApproveUpdateViewForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ['first_rejected', 'first_rejected_comment', 'finally_rejected', 'finally_rejected_comment',
                   'restore_request', 'restore_request_text', 'restored', 'application_date', 'application_update']

    def __init__(self, *args, **kwargs):
        super(ClaimApproveUpdateViewForm, self).__init__(*args, **kwargs)
        self.fields['status'].disabled = True
        self.fields['client'].disabled = True
        self.fields['theme'].disabled = True
        self.fields['text'].disabled = True
        self.fields['priority'].disabled = True
        self.fields['documents'].disabled = True


class CommentCreateViewForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        exclude = ['date_created', 'date_updated', 'author']
        widgets = {'to_claim': forms.HiddenInput()}


# ['theme', 'priority', 'text', 'client', 'application_date', 'application_update', 'status', 'first_rejected', 'finally_rejected',
# 'restored', 'documents']


class ClaimRejectUpdateViewForm(forms.ModelForm):
    first_rejected_comment = forms.CharField(max_length=10000, label='Причина отклонения', widget=forms.Textarea,
                                             required=True)

    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ['finally_rejected', 'finally_rejected_comment', 'restore_request_text', 'restored',
                   'application_date', 'application_update', 'restore_request']

    def __init__(self, *args, **kwargs):
        super(ClaimRejectUpdateViewForm, self).__init__(*args, **kwargs)
        self.fields['status'].disabled = True
        self.fields['first_rejected'].disabled = True
        self.fields['client'].disabled = True
        self.fields['theme'].disabled = True
        self.fields['text'].disabled = True
        self.fields['priority'].disabled = True
        self.fields['documents'].disabled = True


class ClaimFinalRejectUpdateViewForm(forms.ModelForm):
    finally_rejected_comment = forms.CharField(max_length=10000, label='Причина окончательного отклонения',
                                               widget=forms.Textarea, required=True)

    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ['restored', 'application_date', 'application_update']

    def __init__(self, *args, **kwargs):
        super(ClaimFinalRejectUpdateViewForm, self).__init__(*args, **kwargs)
        self.fields['client'].disabled = True
        self.fields['theme'].disabled = True
        self.fields['text'].disabled = True
        self.fields['priority'].disabled = True
        self.fields['documents'].disabled = True
        self.fields['status'].disabled = True
        self.fields['first_rejected'].disabled = True
        self.fields['first_rejected_comment'].disabled = True
        self.fields['restore_request'].disabled = True
        self.fields['restore_request_text'].disabled = True
        self.fields['finally_rejected'].disabled = True


class ClaimRestoreUpdateViewForm(forms.ModelForm):
    restore_request_text = forms.CharField(max_length=10000, label='Причина восстановления', widget=forms.Textarea,
                                           required=True)

    class Meta:
        model = Claim
        fields = '__all__'
        exclude = ['finally_rejected', 'finally_rejected_comment', 'restored',
                   'application_date', 'application_update', 'restore_request']

    def __init__(self, *args, **kwargs):
        super(ClaimRestoreUpdateViewForm, self).__init__(*args, **kwargs)
        self.fields['status'].disabled = True
        self.fields['first_rejected'].disabled = True
        self.fields['first_rejected_comment'].disabled = True
        self.fields['client'].disabled = True
        self.fields['theme'].disabled = True
        self.fields['text'].disabled = True
        self.fields['priority'].disabled = True
        self.fields['documents'].disabled = True
