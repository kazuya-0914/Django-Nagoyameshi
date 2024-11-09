from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic, View

from . import forms
from . import models

class UserDetailView(generic.DeleteView):
    model = models.CustomUser
    template_name = 'user/user_detail.html'

class UserUpdateView(generic.UpdateView):
    model = models.CustomUser
    template_name = 'user/user_update.html'
    form_class = forms.UserUpdateForm

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('user_detail', kwargs={'pk', pk})
  
    def form_valid(self, form):
        return super().form_valid(form)
  
    def form_invalid(self, form):
        return super().form_invalid(form)

class SubscribeRegisterView(View):
    template = 'subscribe/subscribe_register.html'

    def get(self, request):
        context = {}
        return render(self.request, self.template, context)
  
    def post(self, request):
        user_id = request.user.id
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')

        correct_cord_number = '4242424242424242'
        if card_number != correct_cord_number:
            context = {
                'error_message': 'クレジットカード番号が正しくありません'
            }
            return render(self.request, self.template, context)

        models.CustomUser.objects.filter(id=user_id) \
        .update(is_subscribed=True, card_name=card_name, card_number=card_number)
        return redirect(reverse_lazy('top_page'))

class SubscribeCancelView(generic.TemplateView):
    template_name = 'subscribe/subscribe_cancel.html'

    def post(self, request):
        user_id = request.user.id
        models.CustomUser.objects.filter(id=user_id).update(is_subscribed=False)
        return redirect(reverse_lazy('top_view'))
    
class SubscribePaymentView(View):
    template = 'subscribe/subscribe_payment.html'

    def get(self, request):
        user_id = request.user.id
        user = models.CustomUser.objects.get(id=user_id)
        context = {'user': user}
        return render(self.request, self.template, context)

    def post(self, request):
        user_id = request.user.id
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')

        print(card_name, card_number)
        models.CustomUser.objects.filter(id=user_id).update(card_name=card_name, card_number=card_number)

        return redirect(reverse_lazy('top_page'))

