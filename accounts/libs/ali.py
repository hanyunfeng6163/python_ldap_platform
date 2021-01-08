#!/usr/bin/env python
#coding=utf-8
import json
import time

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkram.request.v20150501.CreateUserRequest import CreateUserRequest
from aliyunsdkram.request.v20150501.CreateLoginProfileRequest import CreateLoginProfileRequest
from aliyunsdkram.request.v20150501.DeleteLoginProfileRequest import DeleteLoginProfileRequest
from aliyunsdkram.request.v20150501.DeleteUserRequest import DeleteUserRequest
from aliyunsdkram.request.v20150501.AddUserToGroupRequest import AddUserToGroupRequest
from aliyunsdkram.request.v20150501.RemoveUserFromGroupRequest import RemoveUserFromGroupRequest


class AliRam:
    def __init__(self, access_id, access_key, region='beijing2'):
        self.client = AcsClient(access_id, access_key, region)

    def __do_action(self, request):
        ret = {'status': False}
        try:
            request.set_accept_format('json')
            response = self.client.do_action_with_exception(request)
            ret['status'] = True
            ret['msg'] = json.loads(str(response, encoding='utf-8'))
        except Exception as e:
            print(e)
        return ret

    def create_user(self, username, nickname, email):
        request = CreateUserRequest()
        request.set_accept_format('json')

        request.set_UserName(username)
        request.set_DisplayName(nickname)
        request.set_Email(email)
        return self.__do_action(request)

    def login_profile(self, username, password):
        request = CreateLoginProfileRequest()
        request.set_accept_format('json')

        request.set_UserName(username)
        request.set_Password(password)
        request.set_PasswordResetRequired(True)

        return self.__do_action(request)

    def delete_login_profile(self, username):
        request = DeleteLoginProfileRequest()
        request.set_accept_format('json')

        request.set_UserName(username)

        return self.__do_action(request)

    def delete_user(self, username):
        """删除用户暂时不行，里面有key"""
        request = DeleteUserRequest()
        request.set_accept_format('json')

        request.set_UserName(username)

        return self.__do_action(request)

    def add_user_to_group(self, username, group_name='rds-group'):
        request = AddUserToGroupRequest()
        request.set_accept_format('json')

        request.set_UserName(username)
        request.set_GroupName(group_name)

        return self.__do_action(request)

    def remove_user_from_group(self, username, group_name='rds-group'):
        request = RemoveUserFromGroupRequest()
        request.set_accept_format('json')

        request.set_UserName(username)
        request.set_GroupName(group_name)

        return self.__do_action(request)



if __name__ == '__main__':
    a = AliRam(access_id='', access_key='')
    # print(a.delete_login_profile('hanxueqi'))
    # a.create_user('hanxueqi', '韩雪琪', 'hanxueqi@ttjianbao.com')
    # a.add_user_to_group('hanxueqi')
    result = a.login_profile('hanxueqi','')
    if result['status']:
        pass