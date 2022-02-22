from django.core.paginator import Paginator, Page
from django.db.models import QuerySet

MAX_POST_DISPLAYED: int = 10


def get_paginator(page_number: int,
                  post_list: QuerySet
                  ) -> Page:
    paginator = Paginator(post_list, MAX_POST_DISPLAYED)
    page_posts = paginator.get_page(page_number)
    return page_posts
