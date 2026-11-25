from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, RegistrationForm
from .models import Article, Category, EmailConfirmation


def home_view(request):
    articles = Article.objects.filter(
        is_published=True
    ).select_related("category").order_by("-created_at")
    category_id = request.GET.get("category", "")
    search_query = request.GET.get("q", "").strip()

    if category_id.isdigit():
        articles = articles.filter(category_id=category_id)
    else:
        category_id = ""

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(content__icontains=search_query)
        )

    return render(
        request,
        "news/home.html",
        {
            "articles": articles,
            "categories": Category.objects.all(),
            "selected_category": category_id,
            "search_query": search_query,
        },
    )


def article_detail_view(request, pk):
    article = get_object_or_404(
        Article.objects.select_related("category"),
        pk=pk,
        is_published=True,
    )
    return render(
        request,
        "news/article_detail.html",
        {
            "article": article,
            "comments": article.comments.select_related("user").order_by("-created_at"),
            "comment_form": CommentForm(),
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        confirmation = EmailConfirmation.objects.create(user=user)
        confirmation_url = request.build_absolute_uri(
            reverse("confirm_email", args=[confirmation.token])
        )

        try:
            sent_count = send_mail(
                "Подтверждение регистрации",
                f"Чтобы подтвердить email, перейдите по ссылке:\n{confirmation_url}",
                None,
                [user.email],
                fail_silently=False,
            )
        except (SMTPException, OSError):
            user.delete()
            form.add_error(
                None,
                "Не удалось отправить письмо. Проверьте настройки SMTP и попробуйте снова.",
            )
        else:
            if sent_count:
                return redirect("check_email")
            user.delete()
            form.add_error(None, "Письмо не было отправлено. Проверьте настройки SMTP.")

    return render(request, "news/register.html", {"form": form})


def check_email_view(request):
    return render(request, "news/check_email.html")


def confirm_email_view(request, token):
    confirmation = get_object_or_404(EmailConfirmation, token=token)
    user = confirmation.user
    confirmation.is_confirmed = True
    confirmation.save(update_fields=["is_confirmed"])
    user.is_active = True
    user.save(update_fields=["is_active"])
    messages.success(request, "Email подтверждён. Теперь можно войти.")
    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(request, "news/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")


@login_required
def comment_create_view(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)

    if not EmailConfirmation.objects.filter(
        user=request.user,
        is_confirmed=True,
    ).exists():
        messages.error(request, "Подтвердите email, чтобы оставлять комментарии.")
        return redirect("article_detail", pk=article.pk)

    if request.method != "POST":
        return redirect("article_detail", pk=article.pk)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
        messages.success(request, "Комментарий добавлен.")
        return redirect("article_detail", pk=article.pk)

    return render(
        request,
        "news/article_detail.html",
        {
            "article": article,
            "comments": article.comments.select_related("user").order_by("-created_at"),
            "comment_form": form,
        },
        status=400,
    )
