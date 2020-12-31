import smtplib
from email.header import Header
from email.mime.text import MIMEText


#阿里云企业邮箱相同主题和内容的邮件不能重复发送
# 发件人和收件人
sender = 'hanyunfeng@10dream.com'
receiver = 'hanyunfeng@newlink.com'

# 所使用的用来发送邮件的SMTP服务器
smtpserver = 'smtp.qiye.aliyun.com'

# 发送邮箱的用户名和授权码（不是登录邮箱的密码）
username = 'hanyunfeng@10dream.com'
password = 'Joycareer123'


# 邮件主题
mail_title = '主题：测试报告345'

# 读取html文件内容
mail_body = '<html><h1>你好，我是韩</h1></html>'

# 邮件内容, 格式, 编码
message = MIMEText(mail_body, 'html', 'utf-8')
message['From'] = sender
message['To'] = receiver
message['Subject'] = Header(mail_title, 'utf-8')

try:
    #smtp = smtplib.SMTP(smtpserver, 465)
    smtp = smtplib.SMTP_SSL(smtpserver, 465)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, message.as_string())
    print("发送邮件成功！！！")
    smtp.quit()
except smtplib.SMTPException as e:
    print(e)
    print("发送邮件失败！！！")