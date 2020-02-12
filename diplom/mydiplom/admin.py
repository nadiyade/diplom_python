from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import MyUser, Claim, Comment


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'photo', 'first_name', 'patronymic_name', 'last_name', 'gender', 'email',
                    'birthday', 'country', 'phone_number1', 'phone_number2')
    # list_display = '__all__'

    def photo(self, obj):
        return mark_safe('<img src={url} width="115" height="155"/>'.format(url=obj.photo.url))
    photo.short_description = 'Фото'


class ClaimAdmin(admin.ModelAdmin):
    display = '__all__'


class CommentAdmin(admin.ModelAdmin):
    display = '__all__'
    exclude = ['text']


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Claim, ClaimAdmin)
admin.site.register(Comment, CommentAdmin)
