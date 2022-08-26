from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions

from core.models import User
from .authentication import JWTAuthentication
from .serializers import UserSerializer

class RegisterAPIView(APIView):
    def post(self, request):
        print("Something happenin dog")
        data = request.data # A JSON object is expected with all necessary fields to create a user
        print(data)
        # Receiving the fields is not enough, we also verify that the password confirmation is == password
        if data['password'] != data['password_confirm']:

            raise exceptions.APIException('Password and confirmation password different!')

        # Here we register the users permission dynamically, depending on which api is registering
        data['is_ambassador'] = 'api/ambassador' in request.path

        # TODO Return a response if there's already a user indicating that a user exists
        # TODO Return a response if the passwords are not the same. Ultimately the DB must provide info on failures

        # Here we validate the incoming JSON data and turn it into data types Python can understand.
        # After converting the data it checks to see if it's valid when comparing it to the model we have
        # written in Python. If all checks out then it will try to save it to the db.
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)  # Must be called before calling save()
        serializer.save()

        # return Response(serializer.data)
        return Response(serializer.data)

class LoginAPIView(APIView):
    def post(self, request):

        # Obtain the necessary information to be able to verify a user which is email and password.
        email = request.data["email"]
        password = request.data["password"]

        # Using Djangos filter let's try to find this user in our database
        user = User.objects.filter(email=email).first()

        # If the user was not found then raise an error
        if user is None:
            raise exceptions.AuthenticationFailed("User does not exist in database")
        # If the user is found, then let's use Djangos built in password check method
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Password is incorrect")

        # here we define the scope depending on the request path, this scope is stored in the JWT token
        # and used for authenticating api's
        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        # This prevents users who are registered as ambassadors from registering into an admin api
        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized - this account has ambassador privileges only')

        jwt_token = JWTAuthentication.generate_jwt(user.id, scope)

        # we set httponly to true so that the frontend cannot access the cookie. This cookie is only for the backend
        # to validate making the cookie a bit more secure.
        response = Response()
        response.set_cookie(key='jwt', value=jwt_token, httponly=True)
        response.data = {
            'message': 'success'
        }
        return response


class UserAPIView(APIView):
    # Here we are telling Django we want to use the class we created withing authentication.py to do authentication.
    # This is also why that clas inherits from base authentication and also why we implement the authenticate method
    # so that django knows which method to use for obtaining the cookie, and dealing with the cookie our way.
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(request.user).data

        if 'api/ambassador' in request.path:
            data['revenue'] = user.revenue

        return Response(data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Pretty simple, we create a response object. We tell that object what we want to do is delete the jwt cookie and
    # return that same object. This response tells the browser to delete the cookie.
    def post(self, request):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class UserInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        print(request.data)
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)  # Partial means we only want to update parts
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserPasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] == data['password_confirm']:
            user.set_password(data['password'])
            user.save()
        else:
            raise exceptions.APIException("There is an issue with the passwords!")

        return Response(UserSerializer(user).data)


