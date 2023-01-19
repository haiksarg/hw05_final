from django.conf import settings
from django.core.paginator import Paginator


def paging(request, value):
    paginator = Paginator(value, settings.UPDATETS_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
