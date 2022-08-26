import math, random, time, string

from django_redis import get_redis_connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.authentication import JWTAuthentication
from .serializer import ProductSerializer, LinkSerializer
from core.models import Product, Link, Order, User
from django.core.cache import cache

import time


class ProductFrontendAPIView(APIView):
    @method_decorator(cache_page(60 * 60 * 2, key_prefix='products_frontend'))
    def get(self, _):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductBackendAPIView(APIView):

    def get(self, request):
        # In this simple implementation of caching we attempt to see if there are products already cached in an
        # object named 'products_backend'. If there is not then we do a traditional query to obtain them.
        # The time here is used just to simulate lots of data being processed.
        products = cache.get('products_backend')
        if not products:
            time.sleep(2)
            products = list(Product.objects.all())
            cache.set('products_backend', products, timeout=60*30)

        # Here we obtain a quey parameter from the url. This url contains a substring to search for in the products.
        # using the fact that list data structures are mutable we can perform a filter with a just a few lines.
        s = request.query_params.get('s','')
        if s:
            products = list([
                p for p in products
                if (s.lower() in p.title.lower()) or (s.lower() in p.description.lower())
            ])

        total = len(products)

        # Herer we can sort products using the .sort method built into lists. We use the same quey param as filtering
        sort = request.query_params.get('sort', None)
        if sort == 'asc':
            products.sort(key=lambda p: p.price)
        elif sort == 'desc':
            products.sort(key=lambda p: p.price, reverse=True)

        # Here we have pagination where on the backend we respond with only a page's worth of data.
        per_page = 9
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * per_page
        end = page * per_page

        data = ProductSerializer(products[start:end], many=True).data
        return Response({
            'data': data,
            'meta': {
                'total': total,
                'page': page,
                'last_page': math.ceil(total/per_page)
            }
        })


class LinkAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = LinkSerializer(data={
            'user': user.id,
            'code': ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            'products': request.data['products']
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class StatsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        links = Link.objects.filter(user_id=user.id)

        return Response([self.format(link) for link in links])

    def format(self, link):
        orders = Order.objects.filter(code=link.code, complete=1)

        return {
            'code': link.code,
            'count': len(orders),
            'revenue': sum(o.ambassador_revenue for o in orders)
        }


# This view is different than the rest in that there is no model for this. What this view does
# is get all the ambassadors and rank them based on revenue. Because all users already have a revenue
# property, this is calculated for us every time we access this property.
class RankingsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ambassador = User.objects.filter(is_ambassador=True)
        # response = list({
        #     'name': a.name,
        #     'revenue': a.revenue,
        # } for a in ambassador)
        # response.sort(key=lambda a: a['revenue'], reverse=True)

        # Rather than using the method above, we use the cache to retrieve the values that we need to.
        con = get_redis_connection("default")
        rankings = con.zrevrangebyscore('rankings', min=0, max=10000, withscores=True)

        return Response({
            r[0].decode("utf-8"): r[1] for r in rankings
        })
