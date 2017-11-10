def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    http_host = request.META.get('HTTP_HOST', None)
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        # This is only true for my particular installations.
        server_port = None
        https = request.META.get('HTTP_X_FORWARDED_PROTO') == 'https'
    else:
        server_port = request.META.get('SERVER_PORT')
        https = request.is_secure()
    prepared = {
        'https': 'on' if https else 'off',
        'http_host': http_host,
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    if server_port:
        # Empty port will make a (lonely) colon ':' appear on the URL, so
        # it's better not to include it at all.
        prepared['server_port'] = server_port
    return prepared
