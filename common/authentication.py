import jwt, datetime
from rest_framework.authentication import BaseAuthentication

from rest_framework import exceptions

from app import settings

from core.models import User

class JWTAuthentication(BaseAuthentication):

    # This authenticate method is similar to Java's interface where we can implement a method from the BaseAuthentication
    # class. The benefit of this is that within our views with 1 line we can define what permission is needed for that
    # user to be authenticated
    def authenticate(self, request):
        is_ambassador = 'api/ambassador' in request.path

        token = request.COOKIES.get('jwt')
        print("trying to authenticate!")
        if not token:
            return None

        # Try to get the cookie. Then using jwt built in functions, we can check for an expired token. Remember how
        # we add the time it was created when we created it.
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('authentication expired, please login again')

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid Scope!')

        # At this point all we know is that the token is not expired. Let's try to now query our database using the
        # objects attribute
        user = User.objects.get(pk=payload['user_id'])


        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        print(user)
        return (user, None)


    # Static methods are similar to java static mathods where the method belongs to the class and not the individual
    # objects created by it.
    @staticmethod
    def generate_jwt(id, scope):
        payload = {
            'user_id': id,
            'scope': scope,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
