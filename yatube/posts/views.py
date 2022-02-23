from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from .utils import get_page_obj
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    posts = Post.objects.select_related(
        'author',
        'group'
    ).all()
    page_obj = get_page_obj(request, posts)

    template = 'posts/index.html'

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_page_obj(request, posts)
    template = 'posts/group_list.html'

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page_obj(request, posts)

    template = 'posts/profile.html'
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    author_posts_count = author.posts.count()

    context = {
        'author': author,
        'page_obj': page_obj,
        'author_posts_count': author_posts_count,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    full_post = get_object_or_404(Post, pk=post_id)
    author_posts_count = full_post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = full_post.comments.all()
    template = 'posts/post_detail.html'
    context = {
        'post': full_post,
        'author_posts_count': author_posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
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

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

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
    template = 'posts:post_detail'
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(request, posts)
    template = 'posts/follow.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect(
            'posts:profile',
            username=username
        )
    follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if follower:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect(
            'posts:profile',
            username=username
        )
    following = Follow.objects.filter(user=request.user, author=author)
    following.delete()
    return redirect(
        'posts:profile',
        username=username
    )
