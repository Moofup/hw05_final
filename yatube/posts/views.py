from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, User

MAX_POST_DISPLAYED: int = 10


def get_page(page_number: int,
             post_list: QuerySet,
             max_displayed_posts: int = MAX_POST_DISPLAYED) -> Page:
    paginator = Paginator(post_list, max_displayed_posts)
    page_posts = paginator.get_page(page_number)
    return page_posts


def index(request):
    post_list = Post.objects.select_related(
        'author',
        'group'
    )
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, post_list)

    title = 'Последние обновления на сайте'
    template = 'posts/index.html'

    context = {
        'page_obj': page_obj,
        'title': title,
    }

    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, post_list)

    title = f'Записи сообщества {group.title}'
    template = 'posts/group_list.html'

    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, post_list)

    title = f'Все посты пользователя {author.username}'
    template = 'posts/profile.html'

    author_posts_count = author.posts.count()

    context = {
        'author': author,
        'page_obj': page_obj,
        'title': title,
        'author_posts_count': author_posts_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    full_post = get_object_or_404(Post, pk=post_id)
    author_posts_count = full_post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = full_post.comments.all()
    title = full_post.text
    template = 'posts/post_detail.html'
    context = {
        'title': title,
        'post': full_post,
        'author_posts_count': author_posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None, )
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', request.user)

    form = PostForm()

    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post.save()
            return redirect('posts:post_detail', post.pk)

    template = 'posts/create_post.html'
    is_edit = True
    context = {'form': form, 'is_edit': is_edit}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    context = {}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    ...


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    context = {}
    return render(request, 'posts/unfollow.html', context)
