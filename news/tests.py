from contextlib import redirect_stdout
from io import StringIO

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Article, Category, Comment, EmailConfirmation

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@asia.local",
)
class NewsTests(TestCase):
    def test_model_signals_print_events_to_terminal(self):
        output = StringIO()

        with redirect_stdout(output):
            category = Category.objects.create(name="События")
            article = Article.objects.create(
                title="Тестовая статья",
                category=category,
                content="Текст",
            )
            comment = Comment.objects.create(
                article=article,
                user=User.objects.create_user(
                    username="signal_reader",
                    email="signal_reader@example.com",
                    password="StrongPassword!123",
                ),
                text="Тестовый комментарий",
            )
            comment.delete()

        terminal_output = output.getvalue()
        self.assertIn("[SIGNAL] Создан объект: категория", terminal_output)
        self.assertIn("[SIGNAL] Создан объект: статья", terminal_output)
        self.assertIn("[SIGNAL] Создан объект: комментарий", terminal_output)
        self.assertIn("[SIGNAL] Удаляется объект: комментарий", terminal_output)

    def test_registration_requires_email_confirmation(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "reader",
                "email": "reader@example.com",
                "password1": "StrongPassword!123",
                "password2": "StrongPassword!123",
            },
        )

        self.assertRedirects(response, reverse("check_email"))
        user = User.objects.get(username="reader")
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password("StrongPassword!123"))
        self.assertEqual(len(mail.outbox), 1)

        login_response = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "StrongPassword!123"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))

        confirmation = EmailConfirmation.objects.get(user=user)
        response = self.client.get(
            reverse("confirm_email", args=[confirmation.token])
        )
        self.assertRedirects(response, reverse("login"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        login_response = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "StrongPassword!123"},
        )
        self.assertRedirects(login_response, reverse("home"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_confirmed_user_can_comment_on_article(self):
        user = User.objects.create_user(
            username="commenter",
            email="commenter@example.com",
            password="StrongPassword!123",
        )
        confirmation = EmailConfirmation.objects.create(user=user)
        category = Category.objects.create(name="Новости")
        article = Article.objects.create(
            title="Первая новость",
            category=category,
            content="Текст новости",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("article_detail", args=[article.pk]))
        self.assertContains(response, "подтвердите email")
        response = self.client.post(
            reverse("comment_create", args=[article.pk]),
            {"text": "Полезная новость"},
        )
        self.assertRedirects(response, reverse("article_detail", args=[article.pk]))
        self.assertFalse(Comment.objects.filter(article=article).exists())

        self.client.get(reverse("confirm_email", args=[confirmation.token]))
        self.client.force_login(user)
        response = self.client.post(
            reverse("comment_create", args=[article.pk]),
            {"text": "Полезная новость"},
        )

        self.assertRedirects(response, reverse("article_detail", args=[article.pk]))
        self.assertEqual(Comment.objects.filter(article=article, user=user).count(), 1)

