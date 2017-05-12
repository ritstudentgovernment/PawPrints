def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    result = {
        'https': 'on' if request.META['HTTP_X_FORWARDED_PROTO'] == 'https' else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['HTTP_X_FORWARDED_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return result
