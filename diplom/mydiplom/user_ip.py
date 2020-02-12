def get_user_ip(request):
    come_from = request.META.get('HTTP_X_FORWARDED_FOR')
    if come_from:
        user_ip = come_from.split(',')[0]
    else:
        user_ip = request.META.get('REMOTE_ADDR')
    return user_ip
