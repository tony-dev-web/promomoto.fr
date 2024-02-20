
class AppSettings(object):
    class AuthenticationMethod:
        EMAIL = "email"

    class EmailVerificationMethod:
        OPTIONAL = "optional"


    def __init__(self, prefix):
        self.prefix = prefix
        assert (self.EMAIL_VERIFICATION == "optional") or True
        assert (self.AUTHENTICATION_METHOD == self.AuthenticationMethod.EMAIL or self.EMAIL_REQUIRED)


    def _setting(self, name, dflt):
        from django.conf import settings
        getter = getattr(settings,"ALLAUTH_SETTING_GETTER",lambda name, dflt: getattr(settings, name, dflt),)
        return getter(self.prefix + name, dflt)

    @property
    def EMAIL_VERIFICATION(self):
        return self._setting( "EMAIL_VERIFICATION", "optional")

    @property
    def AUTHENTICATION_METHOD(self):
        return self._setting("AUTHENTICATION_METHOD", "email")

    @property
    def EMAIL_REQUIRED(self):
        return self._setting("EMAIL_REQUIRED", True)

    @property
    def UNIQUE_EMAIL(self):
        return self._setting("UNIQUE_EMAIL", True)

    @property
    def SIGNUP_FORM_CLASS(self):
        return self._setting("SIGNUP_FORM_CLASS", None)
#
    @property
    def USERNAME_REQUIRED(self):
        return self._setting("USERNAME_REQUIRED", True)

    @property
    def PASSWORD_INPUT_RENDER_VALUE(self):
        return self._setting("PASSWORD_INPUT_RENDER_VALUE", False)

    #@property
    #def AUTHENTICATED_LOGIN_REDIRECTS(self):
     #   return self._setting("AUTHENTICATED_LOGIN_REDIRECTS", True)

   # @property
    #def LOGOUT_ON_PASSWORD_CHANGE(self):
      #  return self._setting("LOGOUT_ON_PASSWORD_CHANGE", False)

    @property
    def USER_MODEL_USERNAME_FIELD(self):
        return self._setting("USER_MODEL_USERNAME_FIELD", "username")

    @property
    def USER_MODEL_EMAIL_FIELD(self):
        return self._setting("USER_MODEL_EMAIL_FIELD", "email")

   # @property
    #def SESSION_COOKIE_AGE(self):
       # return self._setting("SESSION_COOKIE_AGE", 3600)

    @property
    def LOGIN_ATTEMPTS_LIMIT(self):
        return self._setting("LOGIN_ATTEMPTS_LIMIT", 5 )

import sys

app_settings = AppSettings("ACCOUNT_")
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings