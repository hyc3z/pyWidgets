import smtplib
import time
import os
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import subprocess
from subprocess import Popen,PIPE

def CommandOutput(command):
    return subprocess.getoutput(command)

class message:

    def __init__(self, From, To, Subject, header_encoding='utf-8'):
        self.init_message = MIMEMultipart()
        self.init_message['From'] = Header(From, header_encoding)
        self.init_message['To'] = Header(To, header_encoding)
        self.init_message['Subject'] = Header(Subject, header_encoding)

    def add_text(self, Text, text_encoding='utf-8'):
        self.init_message.attach(MIMEText(Text+'\n', 'plain', text_encoding))

    def add_file(self, Filename, encoding='utf-8'):
        try:
            att = MIMEText(open(Filename, 'rb').read(), 'base64', encoding)
            att['Content-Type'] = 'application/octet-stream'
            att['Content-Disposition'] = 'attachment; filename="'+Filename+'"'
            self.init_message.attach(att)
        except:
            print('Add file failed.')

    def getobj(self):
        return self.init_message

    def local_dynamic_obj(self, commands):
        for i in commands:
            self.add_text(CommandOutput(i))
        return self.init_message

    def ssh_dynamic_obj(self, sshconn, commands):
        q = sshconn.multiexec(commands)
        for i in q:
            self.add_text(str(i))
        return self.init_message

    def as_string(self):
        return self.init_message.as_string()

class mailobj:
    def __init__(self, mail_addr=None, passwd=None, mail_host=None, port=25):
        if mail_addr is None:
            self.addr = getpass.getpass(prompt='Email address: ')
        else:
            self.addr = mail_addr
        if mail_host is None:
            self.host = getpass.getpass(prompt='Email host: ')
        else:
            self.host = mail_host
        if passwd is None:
            self.passwd = getpass.getpass(prompt='Password: ', stream=None)
        else:
            self.passwd = passwd
        self.smtpObj = smtplib.SMTP()
        self.smtpObj.connect(self.host, port)
        self.smtpObj.login(self.addr, self.passwd)
        print('Login successful.')

    def sendmail(self, messageobj, sender, receivers):
        self.smtpObj.sendmail(sender, receivers, messageobj.as_string())
        return True

    def routine(self, interval,messageobj, sender, receivers):
        self.sendmail(messageobj, sender, receivers)
        time.sleep(interval)