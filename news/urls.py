from django.urls import path

from . import views


urlpatterns = [
    path("", views.home_view, name="home"),
    path("news/<int:pk>/", views.article_detail_view, name="article_detail"),
    path("register/", views.register_view, name="register"),
    path("check-email/", views.check_email_view, name="check_email"),
    path("confirm-email/<uuid:token>/", views.confirm_email_view, name="confirm_email"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("news/<int:pk>/comments/add/", views.comment_create_view, name="comment_create"),
]
