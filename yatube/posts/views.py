from .forms import PostForm, CommentForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Post, Group, User, Follow
from .utils import pagination
from django.urls import reverse


def index(request):
    post_list = Post.objects.all()
    page_obj = pagination(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts_of_group.all()
    page_obj = pagination(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    users_post = author.author_of_posts.all()
    post_count = users_post.count()
    page_obj = pagination(request, users_post)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'context': author,
        'page_obj': page_obj,
        'post_count': post_count,
        'users_post': users_post,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author_posts = post.author.author_of_posts.count()
    context = {
        'post': post,
        'author_posts': author_posts,
        'form': CommentForm(),
        'comments': post.comments.all()
    }
    print(context['comments'])
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    author = request.user
    is_edit = True
    if author != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(
            request,
            template,
            context={'form': form, 'post': post}
        )
    form = PostForm()
    context = {
        'context': author,
        'is_edit': is_edit,
        'form': form,
        'post': post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    author = request.user
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = author
            post.save()
            return redirect(
                reverse(
                    'posts:profile',
                    kwargs={'username': author.username}
                )
            )
        return render(request, template, context={'form': form})
    form = PostForm()
    context = {
        'form': form
    }
    return render(request, template, context)


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
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    page_obj = pagination(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    following = Follow.objects.filter(user=user, author=author)
    if request.user != author and not following.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=author)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    user = request.user
    following = Follow.objects.filter(user=user, author=author)
    if (user != author) and not (following.exists()):
        following.delete()
    return redirect('posts:profile', username=author)
