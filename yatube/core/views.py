from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'path': request.path,
        'code': 404
    }
    return render(request, 'core/eror.html', context, status=404)


def server_error(request):
    return render(request, 'core/eror.html', {'code': 500}, status=500)


def permission_denied(request, exception):
    return render(request, 'core/eror.html', {'code': 403}, status=403)


def bad_request(request, exception):
    return render(request, 'core/eror.html', {'code': 400}, status=400)


def csrf_failure(request, reason=''):
    return render(request, 'core/eror.html', {'code': '403csrf'})
