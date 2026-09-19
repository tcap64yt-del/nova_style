from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        user.email = data.get("email", "")
        user.name = data.get("name", "")

        return user

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user

        if not user.email:
            user.email = sociallogin.account.extra_data.get("email", "")

        if not user.name:
            user.name = (
                sociallogin.account.extra_data.get("name", "")
                or user.email.split("@")[0]
            )

        if not user.referral_code:
            from .models import generate_referral_code
            user.referral_code = generate_referral_code()

        user.set_unusable_password()
        user.save()

        return user