import pymysql.cursors
from django.conf import settings


def yearning_op_add(username, nickname, email):
    connect = pymysql.connect(
        host=settings.Y_HOST,
        port=settings.Y_PORT,
        user=settings.Y_USER,
        password=settings.Y_PASSWORD,
        db=settings.Y_DATABASE,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connect.cursor() as cursor:  # 创建游标
            # 插入数据
            sql = "INSERT INTO `dba_audit`.`core_accounts`(`username`, `password`, `rule`, `department`, `real_name`, " \
                  "`email`, `is_read`) " \
                  "VALUES ('{username}', 'none', 'guest', 'all', '{nickname}', " \
                  "'{email}', 0);".format(username=username,nickname=nickname,email=email)
            print(sql)
            cursor.execute(sql)
            sql1 = "INSERT INTO `dba_audit`.`core_graineds`(`username`, `group`) " \
                   "VALUES ('{username}', '[\"DEV\",\"PROD\",\"Prod_RO\"]');".format(username=username)
            cursor.execute(sql1)
    except Exception as e:
        print(e)
        connect.rollback()  # 事务回滚

    connect.commit()
    connect.close()  # 关闭数据库连接


def yearning_op_del(username):
    connect = pymysql.connect(
        host=settings.Y_HOST,
        port=settings.Y_PORT,
        user=settings.Y_USER,
        password=settings.Y_PASSWORD,
        db=settings.Y_DATABASE,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connect.cursor() as cursor:  # 创建游标
            sql = "DELETE FROM dba_audit.core_accounts WHERE username = '{username}'".format(username=username)
            cursor.execute(sql)
            sql1 = "DELETE FROM dba_audit.core_graineds WHERE username = '{username}'".format(username=username)
            cursor.execute(sql1)
    except Exception as e:
        print(e)
        connect.rollback()  # 事务回滚

    connect.commit()
    connect.close()  # 关闭数据库连接