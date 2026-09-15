from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Like,Comment,Follow


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')

    return render(request, 'social/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.error(request, 'Invalid username or password.')
        return redirect('login')

    return render(request, 'social/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def home(request):
    posts = Post.objects.all().order_by('-created_at')

    following_ids = []

    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

    return render(request, 'social/home.html', {
        'posts': posts,
        'following_ids': following_ids
    })

@login_required(login_url='/login/')
def create_post(request):

    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Post.objects.create(
                user=request.user,
                content=content
            )

        return redirect('home')

    return redirect('home')

@login_required(login_url='/login/')
def like_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user
    )

    if not created:
        like.delete()

    return redirect('home')

@login_required(login_url='/login/')
def add_comment(request, post_id):

    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('comment')

        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

    return redirect('home')

@login_required(login_url='/login/')
def follow_user(request, user_id):

    user_to_follow = get_object_or_404(User, id=user_id)

    if request.user != user_to_follow:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow.delete()

    return redirect('home')

@login_required(login_url='/login/')
def profile(request, username):

    profile_user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'posts': posts
    })
