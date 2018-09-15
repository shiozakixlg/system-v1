# -*-coding:utf-8 -*-
import jwt, datetime, time
from django.conf import settings
from yqdata.models import User,Role_Authority
from mongoengine.queryset.visitor import Q

class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=360000),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            token = jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
            return token
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, settings.SECRET_KEY, leeway=datetime.timedelta(seconds=10))
            # 取消过期时间验证
            # payload = jwt.decode(auth_token, settings.SECRET_KEY, options={'verify_exp': False})
            if ('data' in payload and 'id' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    @staticmethod
    def authenticate(self, username, password):
        """
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        token = ''
        userInfo = User.objects(Q(user_account=username)).first()
        if (userInfo is None):
            return {
                   "status": False,
                   "token": token,
                   "msg": '找不到用户'
               }
        else:
            if (userInfo.user_passwd == password):
                login_time = int(time.time())
                userInfo.user_logintime = login_time
                # print dir(userInfo)
                userInfo.save()
                role = Role_Authority.objects(Q(role_id=userInfo.user_role_id)).first()
                # userInfo.update(set__user_logintime=login_time)
                token = self.encode_auth_token(userInfo.user_id, login_time)
                authority = role.authority_id
                return {
                       "status": True,
                       "user_name": userInfo.user_account,
                       "user_authority":authority,
                       "token": token,
                       "msg": '成功登录'
                   }
            else:
                return {
                       "status": False,
                       "token": token,
                       "msg": '密码不正确'
                   }

    def identify(self, request):
        """
        用户鉴权
        :return: list
        """
        auth_header = request.headers.get('Authorization')
        if (auth_header):
            auth_tokenArr = auth_header.split(" ")
            if (not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2):
                result = common.falseReturn('', '请传递正确的验证头信息')
            else:
                auth_token = auth_tokenArr[1]
                payload = self.decode_auth_token(auth_token)
                if not isinstance(payload, str):
                    user = Users.get(Users, payload['data']['id'])
                    if (user is None):
                        result = common.falseReturn('', '找不到该用户信息')
                    else:
                        if (user.login_time == payload['data']['login_time']):
                            result = common.trueReturn(user.id, '请求成功')
                        else:
                            result = common.falseReturn('', 'Token已更改，请重新登录获取')
                else:
                    result = common.falseReturn('', payload)
        else:
            result = common.falseReturn('', '没有提供认证token')
        return result
