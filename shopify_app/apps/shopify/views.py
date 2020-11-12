import binascii
import hashlib
import hmac
import os

import shopify
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from shopify_app.apps.shopify.forms import Login as LoginForm


def shopify_session(shop_url):
    api_version = "unstable"
    return shopify.Session(shop_url, api_version)


class Login(FormView):
    template_name = "shopify/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        # Get the shop URL from post data
        shop_url = self.request.POST.get('shop').strip()

        redirect_uri = f"https://{settings.SITE_URL}{reverse('shopify:finalise')}"

        scope = settings.SHOPIFY_API_SCOPE.split(',')

        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

        permission_url = shopify_session(shop_url).create_permission_url(scope, redirect_uri, state)

        return redirect(permission_url)


class Finalise(View):
    def get(self, request):

        params = request.GET.dict()

        myhmac = params.pop('hmac')
        line = '&'.join([
            '%s=%s' % (key, value)
            for key, value in sorted(params.items())
        ])

        h = hmac.new(settings.SHOPIFY_API_SECRET.encode('utf-8'), line.encode('utf-8'), hashlib.sha256)

        if not hmac.compare_digest(h.hexdigest(), myhmac):
            print("Could not verify a secure login")
            return redirect(reverse("shopify:login"))

        try:
            shop_url = params['shop']
            session = shopify_session(shop_url)
            request.session['shopify'] = {
                "shop_url": shop_url,
                "access_token": session.request_token(request.GET)
            }
        except Exception:
            print("Could not log in to Shopify store.")
            return redirect(reverse("shopify:login"))
        print("Logged in to shopify store.")
        request.session.pop('return_to', None)
        return redirect(request.session.get('return_to', reverse('')))
