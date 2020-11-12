import shopify
from django.conf import settings


class Shopify(object):
    def __init__(self, get_response):
        self.get_response = get_response

        self.api_key = settings.SHOPIFY_API_KEY
        self.api_secret = settings.SHOPIFY_API_SECRET

        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)

    def __call__(self, request):
        if hasattr(request, 'session') and 'shopify' in request.session:
            print('Hello from middleware')
            api_version = settings.SHOPIFY_API_VERSION
            shop_url = request.session['shopify']['shop_url']
            shopify_session = shopify.Session(shop_url, api_version)
            shopify_session.token = request.session['shopify']['access_token']
            shopify.ShopifyResource.activate_session(shopify_session)
        response = self.get_response(request)
        shopify.ShopifyResource.clear_session()
        return response
