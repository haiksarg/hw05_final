from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page
from django.db.models.query import QuerySet

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import paging


@cache_page(20, key_prefix="index_page")
def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = paging(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, group_list):
    group = get_object_or_404(Group, slug=group_list)
    posts = group.posts.select_related('author').all()
    page_obj = paging(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group').all()
    page_obj = paging(request, posts)
    followings = len(
        Follow.objects.select_related('author').filter(user=author))
    followers = len(
        Follow.objects.select_related('author').filter(author=author))
    following: QuerySet = {}
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
        'followings': followings,
        'followers': followers,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.all().filter(post__exact=post)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user)
    page_obj = paging(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = len(Follow.objects.filter(
        user=request.user,
        author=author))
    if request.user != author and follow == 0:
        Follow.objects.create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author).delete()
    return redirect('posts:profile', username)
