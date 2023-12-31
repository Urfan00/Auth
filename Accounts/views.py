from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Users
from .serializers import UserSerialzier
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = Users.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        # token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8') ????????
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.data = {
            'jwt': token
        }

        response.set_cookie(key='jwt', value=token, httponly=True)

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        
        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')

        user = Users.objects.filter(id = payload['id']).first()
        serializer = UserSerialzier(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message':'success'
        }

        return response
