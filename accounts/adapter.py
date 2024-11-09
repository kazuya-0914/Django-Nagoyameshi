from allauth.account.adapter import DefaultAccountAdapter

class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):

        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)
        user.user_name = form.cleaned_data.get('user_name')
        user.hurigana = form.cleaned_data.get('hurigana')
        user.zip_code = form.cleaned_data.get('zip_code')
        user.address = form.cleaned_data.get('address')
        user.phone_number = form.cleaned_data.get('phone_number')
        user.birthday = form.cleaned_data.get('birthday')
        user.job = form.cleaned_data.get('job')
        user.is_subscribed = form.cleaned_data.get('is_subscribed')
        user.save()
