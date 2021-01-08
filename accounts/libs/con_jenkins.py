# coding:utf-8
import os

from django.conf import settings


# # jenkins配置
# import configparser
# config = configparser.ConfigParser()
# config.read('../../online.conf')
# JENKINS_URL = config.get('jenkins', 'JENKINS_URL')
# JENKINS_USERNAME = config.get('jenkins', 'JENKINS_USERNAME')
# JENKINS_PASSWORD = config.get('jenkins', 'JENKINS_PASSWORD')
from accounts.libs import jenkins


class JenkinsApi:
    def __init__(self):
        url = settings.JENKINS_URL
        username = settings.JENKINS_USERNAME
        password = settings.JENKINS_PASSWORD
        # url = JENKINS_URL
        # username = JENKINS_USERNAME
        # password = JENKINS_PASSWORD
        self.server = jenkins.Jenkins(url, username=username, password=password)

    def get_role(self, type_name, role_name):
        return self.server.get_role(type_name, role_name)

    def assign_role(self, type_name, role_name, sid):
        return self.server.assign_role(type_name, role_name, sid)

    def unassign_role(self, type_name, role_name, sid):
        return self.server.unassign_role(type_name, role_name, sid)

    def delete_sid(self, type_name, sid):
        return self.server.delete_sid(type_name, sid)

    def get_version(self):
        return self.server.get_version()

    def get_jobs(self):
        return self.server.get_jobs()

    def trigger_job(self, job_name, arg):
        build = self.server.build_job(job_name, arg)
        return build

    def get_build_status(self, job_name, build):
        status = self.server.get_build_info(job_name, build)['result']
        return status

    def get_job_info(self, job_name):
        pass

    def get_job_log(self, job_name, build_id):
        try:
            bulid_logs = self.server.get_build_console_output(job_name, int(build_id))
        except Exception as err:
            bulid_logs = "日志获取失败%s" % err
        return bulid_logs


if '__main__' == __name__:
    a = JenkinsApi()
    #print(a.get_version())
    #print(a.get_role('globalRoles','READ'))
    # print(a.assign_role('globalRoles','READ','hanxueqi'))
    print(a.delete_sid('globalRoles','hanxueqi'))