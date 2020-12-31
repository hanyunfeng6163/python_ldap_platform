# 基于django3的ldap管理平台
> python3.7.9


* [x] 多ldap组织和用户管理
* [x] 用户自行重置或修改密码
* [ ] 集成本地用户支持单点登录

# ldap配置前提
```
# 条目 1: ou=Group,dc=domain,dc=com
dn: ou=Group,dc=domain,dc=com
objectclass: top
objectclass: organizationalUnit
ou: Group


# 条目 1: ou=People,dc=domain,dc=com
dn: ou=People,dc=domain,dc=com
objectclass: top
objectclass: organizationalUnit
ou: People
```

# 简单安装
**参考example.conf 在根目录创建online.conf 修改所需要的配置**
```shell
# 依赖安装
pip install -r requirements.txt
# 库迁移
python manage.py makemigrations 
python manage.py migrate 
# 管理用户创建
python manage.py createsuperuser
# 启动
python3 manage.py runserver 0.0.0.0:8888
```

# coding地址
https://hanyunfeng.coding.net/public/public/python_ldap_platform/git/files


## screenshots
###### 登录
![](http://81.68.127.45:90/screenshots/登录.png)
<img width="400" src="http://81.68.127.45:90/screenshots/登录.png"> 

###### 个人信息
<img width="800" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/个人信息.png"> 

###### 修改密码
<img width="800" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/修改密码.png"> 

###### ldap列表
<img width="800" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/ldap列表1.png"> 

###### ldap管理页
<img width="800" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/ldap管理页.png"> 

###### ldap用户编辑
<img width="500" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/ldap用户编辑.png"> 

###### 重置密码邮件
<img width="800" src="https://hanyunfeng.coding.net/p/public/d/python_ldap_platform/git/raw/main/screenshots/重置密码邮件.png"> 


