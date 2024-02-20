from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from compte.account import views


urlpatterns = [
    path("compte/signup/", views.SignupView.as_view(), name="account_signup"),
    path("compte/login/", views.LoginView.as_view(), name="account_login"),
    path("compte/logout/", login_required(views.LogoutView.as_view()), name="account_logout"),
    path("compte/password/reset/", views.PasswordResetView.as_view(), name="account_reset_password"),
    path("compte/password/reset/done/", views.PasswordResetDoneView.as_view(), name="account_reset_password_done", ),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",views.PasswordResetFromKeyView.as_view(),name="account_reset_password_from_key",),
    re_path(r"^confirm-email/(?P<key>[-:\w]+)/$",views.ConfirmEmailView.as_view(),name="account_confirm_email",),
    #path("compte/inactif/", login_required(views.AccountInactiveView.as_view()), name="account_inactive"),

]