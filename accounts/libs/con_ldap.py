# Modified from bigyong.cn
import json
from functools import reduce

from ldap3 import Server, Connection, NTLM, ALL_ATTRIBUTES, HASHED_SALTED_SHA256, HASHED_MD5, HASHED_NONE, \
    MODIFY_REPLACE, BASE, MODIFY_ADD, SUBTREE, MODIFY_DELETE


def group_dn_magic_re(group_dn):
    group_info_list = [x.split('=')[1] for x in group_dn.split(',') if x.startswith('cn')]
    cns = '-' + ('-').join(group_info_list[::-1])
    return cns


def group_dn_magic(group_dn, ldap_group_dn):
    """
    -技术部-运维部 转 cn=运维部,cn=技术部,ou=Group,dc=10dream,dc=com
    :param group_dn:
    :param ldap_group_dn:  like ou=Group,dc=10dream,dc=com
    :return:
    """
    cns = ''
    all_cn = group_dn.split('-')
    all_cn.reverse()  # 倒序，注意结果直接在原来的列表里
    for i in all_cn:
        if i != '':
            cns += 'cn={},'.format(i)
    cns += ldap_group_dn
    return cns


def update_dict(result_dict, in_dict):
    for k, v in in_dict.items():
        if k in result_dict:
            update_dict(result_dict[k], in_dict[k])
        else:
            result_dict[k] = v
    return result_dict


def update_tree_json(d, upper_key=''):
    """
    后面这个函数要处理菜单展开 active等功能
    result = []
    for k, v in d.items():
        one_dict = dict()
        one_dict['text'] = k
        one_dict['icon'] = 'fa fa-folder-o'
        if v:
            one_dict['nodes'] = update_tree_json(v, now_department)
        result.append(one_dict)
    return result
    :param d , upper_key:
    :return:
    """
    # result = []
    # active_status = False
    # for k, v in d.items():
    #     one_dict = dict()
    #     one_dict['text'] = k
    #     one_dict['icon'] = 'fa fa-folder-o'
    #     if k == now_department:
    #         active_status = True
    #         one_dict['class'] = 'active'
    #
    #     if v:
    #         x = update_tree_json(v, now_department)
    #         if x[0]:
    #             one_dict['show'] = True
    #             active_status = True
    #         one_dict['nodes'] = x[1]
    #     result.append(one_dict)
    # return active_status ,result

    # 下面这段代码，是拼装部门树的基础方法，但是当前端要选定某个节点，并选中的时候，就不能返回active等信息了,但是使用jstree不需要上面的方法，上面用的是bstreeview
    # result = []
    # for k, v in d.items():
    #     one_dict = dict()
    #     one_dict['text'] = k
    #     one_dict['icon'] = 'fa fa-folder-o'
    #     if v:
    #         one_dict['nodes'] = update_tree_json(v)
    #     result.append(one_dict)
    # return result

    # 增加了upper_key 用来区分不同分组但是同名的问题
    result = []
    for k, v in d.items():
        one_dict = dict()
        one_dict['id'] = '{}-{}'.format(upper_key, k)
        one_dict['text'] = k
        if v:
            one_dict['children'] = update_tree_json(v, upper_key='{}-{}'.format(upper_key, k))
        result.append(one_dict)
    return result


def update_menu_tree_json(d, group_dn, upper_key=''):
    """
    传入group_dn，当编辑当前部门上级部门的时候，不能把自己的子部门信息让用户选择，所有当节点到达groupdn后，进行continue操作进行拦截
    :param d:
    :param group_dn:
    :param upper_key:
    :return:
    """
    result = []
    for k, v in d.items():
        one_dict = dict()
        one_dict['id'] = '{}-{}'.format(upper_key, k)
        one_dict['title'] = k
        if group_dn == '{}-{}'.format(upper_key, k):
            continue  # 这里的continue很重要，如何使用break；后面的正常树也被中断了
        if v:
            one_dict['subs'] = update_menu_tree_json(v, group_dn, upper_key='{}-{}'.format(upper_key, k))
        result.append(one_dict)
    return result


class AD(object):
    def __init__(self, host, port, user, password, base_dn, ldap_server='openladp', use_ssl=False,
                 ldap_user_object_class='inetOrgPerson',
                 ldap_group_object_class='groupOfUniqueNames',):
        if ldap_server == 'windows_ad':
            authentication = NTLM
        else:
            authentication = None
        _server = Server(
            host=host,
            port=port,
            use_ssl=use_ssl,
            connect_timeout=5,
        )
        self.conn = Connection(  # 配置服务器连接参数
            server=_server,
            auto_bind=True,
            authentication=authentication,  # 连接Windows AD需要配置此项
            read_only=False,  # 禁止修改数据：True
            user=user,  # 管理员账户
            password=password,
        )

        self.server = _server

        self.people_base = 'ou=People,{base_dn}'.format(base_dn=base_dn)  # 用户
        self.group_base = 'ou=Group,{base_dn}'.format(base_dn=base_dn)  # 组
        self.ldap_user_object_class = ldap_user_object_class
        self.ldap_group_object_class = ldap_group_object_class

        self.people_search_filter = '(objectclass={})'.format(ldap_user_object_class)  # 获取用户对象
        self.group_search_filter = '(objectclass={})'.format(ldap_group_object_class)  # 获取组对象

        self.ldap_user_password = 'joycareer'

    def search_group_info(self):
        """
        废弃方法
        search_scope=BASE 不搜索包含的子树
        search_scope=SUBTREE (默认) 包含子树
        :return:
        """
        self.conn.search(search_base='cn=运维部,cn=技术部,{}'.format(self.group_base),
                         search_filter=self.group_search_filter, attributes=ALL_ATTRIBUTES, search_scope=BASE)
        res = self.conn.response_to_json()
        res = json.loads(res)['entries']
        return res

    def search_user_groups(self, username):
        """
        获取当前用户的全部部门，在编辑用户的时候会需要
        username like 曹兴
        :param username:
        :return:
        """
        search_filter = '(|(&(objectclass={ldap_group_object_class})(uniqueMember=cn={username},{people_base})))'.format(
            username=username, people_base=self.people_base, ldap_group_object_class=self.ldap_group_object_class)
        self.conn.search(search_base=self.group_base,
                         search_filter=search_filter, attributes=ALL_ATTRIBUTES, search_scope=SUBTREE)
        res = self.conn.response_to_json()
        res = json.loads(res)['entries']
        return res

    def search_group_user_list(self, dn):
        """
        传入group，返回下面的user list详细信息；并且拼接成和get_user_list方法返回一样的结构
        :return:
        """
        self.conn.search(search_base=dn,
                         search_filter=self.group_search_filter, attributes=ALL_ATTRIBUTES, search_scope=BASE)
        res = self.conn.response_to_json()
        res = json.loads(res)['entries'][0]['attributes']['uniqueMember']
        user_list = []
        for i in res:
            if i != 'cn=base,{}'.format(self.people_base):
                status, msg = self._search_user_info(dn=i)
                if status:
                    user_list.append(msg)
        return user_list

    def search_user_info(self, cn):
        """
        :return:
        """
        dn = 'cn={cn},{people_base}'.format(cn=cn, people_base=self.people_base)
        try:
            self.conn.search(search_base=dn,
                             search_filter=self.people_search_filter, attributes=ALL_ATTRIBUTES)
            res = self.conn.response_to_json()
            res = json.loads(res)['entries'][0]['attributes']
            return True, res
        except:
            return False, 'err'

    def _search_user_info(self, dn):
        """
        :return:
        """
        try:
            self.conn.search(search_base=dn,
                             search_filter=self.people_search_filter, attributes=ALL_ATTRIBUTES)
            res = self.conn.response_to_json()
            res = json.loads(res)['entries'][0]
            return True, res
        except:
            return False, 'err'

    def get_user_list(self):
        """
        获取所有用户
        :return:
        """
        self.conn.search(search_base=self.people_base, search_filter=self.people_search_filter,
                         attributes=ALL_ATTRIBUTES, paged_size=1000)
        res = self.conn.response_to_json()
        a = self.conn.result
        # a = self.conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        # print(str(a, encoding="utf-8"))
        res = json.loads(res)['entries']
        # 剔除用户列表里的base用户
        res_no_with_base = [x for x in res if x['dn'] != 'cn=base,{people_base}'.format(people_base=self.people_base)]
        return res_no_with_base

    def get_group_list(self):
        """
        获取所有组
        :return:
        """
        self.conn.search(search_base=self.group_base, search_filter=self.group_search_filter, attributes=ALL_ATTRIBUTES)
        res = self.conn.response_to_json()
        res = json.loads(res)['entries']
        return res

    def get_group_tree_json(self):
        department_dict = {}
        dn_list = [x['dn'] for x in self.get_group_list()]
        for one_dn in dn_list:
            a = [x.split('=')[1] for x in one_dn.split(',') if x.startswith('cn')]
            d = reduce(lambda x, y: {y: x}, a, {})
            department_dict = update_dict(department_dict, d)
        return update_tree_json(department_dict)

    def get_group_menu_tree_json(self, group_dn):
        """
        在编辑部门时返回给前端一个部门树，并且返回结果不包含当前部门的子部门
        :param group_dn:
        :return:
        """
        department_dict = {}
        dn_list = [x['dn'] for x in self.get_group_list()]
        for one_dn in dn_list:
            a = [x.split('=')[1] for x in one_dn.split(',') if x.startswith('cn')]
            d = reduce(lambda x, y: {y: x}, a, {})
            department_dict = update_dict(department_dict, d)

        return update_menu_tree_json(department_dict, group_dn)

    def get_user_menu_tree_json(self):
        """
        在新建用户的时候返回一个部门树
        :return:
        """
        department_dict = {}
        dn_list = [x['dn'] for x in self.get_group_list()]
        for one_dn in dn_list:
            a = [x.split('=')[1] for x in one_dn.split(',') if x.startswith('cn')]
            d = reduce(lambda x, y: {y: x}, a, {})
            department_dict = update_dict(department_dict, d)

        return update_menu_tree_json(department_dict, '')

    def create_obj(self, dn, obj_type, attr=None, new_password='joycareer'):
        """
        新建用户or 部门，User需要设置密码，激活账户
        :param dn: dn = "ou=人事部3,ou=罗辑实验室,dc=adtest,dc=intra"  # 创建的OU的完整路径
                   dn = "cn=张三,ou=人事部3,ou=罗辑实验室,dc=adtest,dc=intra"  # 创建的User的完整路径
        :param obj_type:选项：ou or user
        :param new_password:选项：ou or user
        :param attr = {#User 属性表，需要设置什么属性，增加对应的键值对
                        "SamAccountName": "zhangsan",  # 账号
                        "EmployeeID":"1",    # 员工编号
                        "Sn": "张",  # 姓
                        "name": "张三",
                        "telephoneNumber": "12345678933",
                        "mobile": "12345678933",
                        "UserPrincipalName":"zhangsan@adtest.com",
                        "Mail":"zhangsan@adtest.com",
                        "Displayname": "张三",
                        "Manager":"CN=李四,OU=人事部,DC=adtest,DC=com",#需要使用用户的DN路径
                    }
                attr = {#OU属性表
                        'name':'人事部',
                        'managedBy':"CN=张三,OU=IT组,OU=罗辑实验室,DC=adtest,DC=intra", #部分负责人
                        }

        :return:True and success 是创建成功了
        (True, {'result': 0, 'description': 'success', 'dn': '', 'message': '', 'referrals': None, 'type': 'addResponse'})

        """
        # 区分类型是用户user，还是组ou
        object_class = {
            'user': ['inetOrgPerson', 'top'],
            'ou': ['groupOfUniqueNames', 'top'],
        }
        res = self.conn.add(dn=dn, object_class=object_class[obj_type], attributes=attr)
        if res and obj_type == "user":
            self.conn.extend.standard.modify_password(dn, None, new_password)
        return res, self.conn.result

    def modify_password(self, dn, newpassword):
        """
        重置密码
        :param dn:
        :param newpassword:
        :return:
        """
        res = self.conn.extend.standard.modify_password(dn, None, newpassword)
        return res, self.conn.result

    def del_obj(self, DN):
        """
        删除用户 or 部门
        :param DN:
        :return:True
        """
        res = self.conn.delete(dn=DN)
        return res

    def update_obj(self, dn, attr):
        """更新员工 or 部门属性
        先比较每个属性值，是否和AD中的属性一致，不一样的记录，统一update
        注意：
            1. attr中dn属性写在最后
        User 的 attr 照如下格式写：
        dn = "cn=test4,ou=IT组,dc=adtest,dc=com" #需要移动的User的原始路径
        {#updateUser需要更新的属性表
             "Sn": "李",  # 姓
             "telephoneNumber": "12345678944",
             "mobile": "12345678944",
             "Displayname": "张三3",
             "Manager":"CN=李四,OU=人事部,DC=adtest,DC=com",#需要使用用户的DN路径
            }

        OU 的 attr 格式如下：
        dn = "ou=人事部,dc=adtest,dc=com" #更新前OU的原始路径
        attr = {
        'name':'人事部',
        'managedBy':"CN=张三,OU=IT组,DC=adtest,DC=com",
        }
        """
        try:
            for k, v in attr.items():
                if not self.conn.compare(dn=dn, attribute=k, value=v):
                    changes_dic = {}
                    changes_dic.update({k: [(MODIFY_REPLACE, [v])]})
                    self.conn.modify(dn=dn, changes=changes_dic)
            return True
        except Exception as e:
            return False

    def group_add_user(self, dn, attr):
        """
        在部门里添加用户，不是替换，上面的update_obj是替换attr配置了
        :param dn:
        :param attr:
        :return:
        """
        changes_dic = {}
        for k, v in attr.items():
            if not self.conn.compare(dn=dn, attribute=k, value=v):  # 判断当前dn没有，则创建
                changes_dic.update({k: [(MODIFY_ADD, [v])]})
                # print(changes_dic)
                self.conn.modify(dn=dn, changes=changes_dic)
        return self.conn.result

    def group_del_user(self, dn, attr):
        """
        在部门里删除用户，不是替换，上面的update_obj是替换attr配置了
        :param dn:
        :param attr:
        :return:
        """
        changes_dic = {}
        for k, v in attr.items():
            if self.conn.compare(dn=dn, attribute=k, value=v):  # 判断当前dn里有，则删除
                changes_dic.update({k: [(MODIFY_DELETE, [v])]})
                self.conn.modify(dn=dn, changes=changes_dic)
        return self.conn.result

    def update_group_name_or_upper(self, old_dn, new_dn):
        """
        修改组名或者上级组织
        :return:
        """
        # 先改名
        status = False
        try:
            new_name = new_dn.split(",", 1)[0]
            old_ou_dc = old_dn.split(",", 1)[1]
            rename_result = self.rename_obj(old_dn, new_name)
            if rename_result['description'] == 'success':
                if self.move_object(new_name + ',' + old_ou_dc, new_dn):
                    status = True
        except Exception as e:
            print(e)
        return status
        # # 后移动
        # if self.move_object(old_dn, new_dn):
        #     self.rename_obj()
        # else:
        #     return False

    def rename_obj(self, dn, new_name):
        """
        OU or User 重命名方法用法：
        rename_obj('cn=曹2,ou=People,dc=10dream,dc=com','cn=曹行')
        :param dn:需要修改的object的完整dn路径
        :param newname: 新的名字，User格式："cn=新名字";OU格式："OU=新名字"
        :return:返回中有：'description': 'success', 表示操作成功
        {'result': 0, 'description': 'success', 'dn': '', 'message': '', 'referrals': None, 'type': 'modDNResponse'}
        """

        self.conn.modify_dn(dn, new_name)
        return self.conn.result

    def move_object(self, dn, new_dn):
        """
        移动员工 or 部门到新部门
        :param dn:
        :param new_dn:
        :return:
        """
        relative_dn, superou = new_dn.split(",", 1)
        res = self.conn.modify_dn(dn=dn, relative_dn=relative_dn, new_superior=superou)
        return res

    def check_password(self, username, password):
        try:
            dn = 'cn={username},{people_base}'.format(username=username, people_base=self.people_base)
            conn2 = Connection(self.server, user=dn, password=password, check_names=True, lazy=False,
                               raise_exceptions=False)
            conn2.bind()
            if conn2.result["description"] == "success":
                status, user_info = self.search_user_info(username)
                if status:
                    django_user = {}
                    django_user['username'] = username
                    try:
                        django_user['nickname'] = user_info['displayName']
                    except Exception as e:
                        django_user['nickname'] = username
                    try:
                        django_user['email'] = user_info['mail'][0]
                    except Exception as e:
                        django_user['email'] = ''
                    try:
                        django_user['phone'] = user_info['telephoneNumber'][0]
                    except Exception as e:
                        django_user['phone'] = ''
                    return True, django_user
                else:
                    return False, '用户认证成功，但信息获取失败'
            else:
                return False, '用户认证失败'
        except Exception as e:
            print(e)
            return False, '未知错误，需要联系管理员'


if __name__ == '__main__':
    ad = AD(host='', port=389, user='cn=Manager,dc=10dream,dc=com', password='', base_dn='dc=xxx,dc=com')
    # print(ad.get_group_list())
    # print(ad.search_group_user_list())
    # print(ad.search_user_info(cn='dengyong'))
    # ad.get_user_list()

    # print(ad.create_obj("cn=中台基础,cn=技术部,ou=Group,dc=10dream,dc=com", "ou", attr={'uniqueMember':'cn=base,ou=People,dc=10dream,dc=com'}))
    # print(ad.create_obj("cn=wangcongxin,ou=People,dc=10dream,dc=com", "user",
    #                     attr={'sn': 'wang', 'givenName': 'congxin', 'displayName': '王从新',
    #                           'mail': 'wangcongxin@10dream.com', 'telephoneNumber': '12833221122',
    #                           }))
    # 邮箱 中文名 电话 部门（多选）
    # print(ad.create_obj("cn=陈洪安,ou=People,dc=10dream,dc=com", "user", attr={'sn':'chenhongan'}))
    # print(ad.del_obj('cn=张贺鹏,ou=People,dc=10dream,dc=com'))
    # print(ad.update_obj('cn=曹兴,ou=People,dc=10dream,dc=com',attr={'telephoneNumber':'12','mail':'caoxing@10dream.com'}))
    # print(ad.group_add_user('cn=技术部,ou=Group,dc=10dream,dc=com',attr={'uniqueMember':'cn=曹兴,ou=People,dc=10dream,dc=com'}))
    # print(ad.group_del_user('cn=技术部,ou=Group,dc=10dream,dc=com',
    #                        attr={'uniqueMember': 'cn=曹兴,ou=People,dc=10dream,dc=com'}))
    # print(ad.get_group_tree_json())
    # print(ad.get_group_menu_tree_json('-技术部-运维部'))
    # print(ad.rename_obj('cn=曹星,ou=People,dc=10dream,dc=com','cn=曹兴'))
    # ad.move_object('cn=曹兴,ou=Group,dc=10dream,dc=com','cn=曹兴,ou=People,dc=10dream,dc=com')
    # ad.update_group_name_or_upper('cn=运维部5,cn=技术部,ou=Group,dc=10dream,dc=com','cn=运维部,cn=产品中心,ou=Group,dc=10dream,dc=com')
    # print(ad.search_user_groups('曹兴'))
    # print(ad.search_user_info('dengyong'))
    # print(ad.check_password('dengyong', 'joycareer'))
    print(ad.modify_password('cn=dengyong,ou=People,dc=10dream,dc=com', 'Joycareer123'))
