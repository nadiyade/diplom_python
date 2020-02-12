from django.core.exceptions import ValidationError


def file_size(value):
    limit = 15 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 15 MB.')


def photo_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 2 MB.')
