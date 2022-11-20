from django.core.paginator import Paginator


AMOUNT_POSTS_ON_PAGE = 10


def pagination(request, post):
    paginator = Paginator(post, AMOUNT_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
