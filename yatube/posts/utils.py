from django.core.paginator import Paginator, Page
from django.db.models import QuerySet

MAX_POST_DISPLAYED: int = 10


def get_page_obj(request,
                 post_list: QuerySet) -> Page:
    paginator = Paginator(post_list, MAX_POST_DISPLAYED)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)
    return page_posts
