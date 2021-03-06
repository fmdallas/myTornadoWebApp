__author__ = 'Jacklam'

import sys
import time
from email.mime.text import MIMEText
from smtpFactory import SmtpServerFactory


class EmailSender:
    def __init__(self, serverFactory=SmtpServerFactory):
        # initialize a server factory
        self.serverFactory = serverFactory

    def set_smtp_server(self, hostname, verbose=True):
        # get a server randomly by parsing the host name of server
        self.hostname = hostname
        factory = self.serverFactory(hostname)
        self.server = factory.get_server(hostname)

        if not self.server:
            sys.exit(0)

        if verbose:
            self.server.set_debuglevel(1)

    def login_to_server(self, username, password):
        # login to server with username, password
        self.username = username
        self.password = password
        self.server.local_hostname = 'Greetings-miao'
        self.server.login(username, password)
        print "login success to %s!" % username

    def reconnect_to_server(self, hostname, username, password):
        # reconnect to smtp server with hostname, username, password
        self.server = self.set_smtp_server(hostname)
        self.login_to_server(username, password)

    def set_html_template(self, html_template, **kwargs):
        # substitute key value pairs
        for k,v in kwargs.items():
            html_template = html_template.replace(k,v)
        return html_template

    def set_mime_message(self, subject, from_, to_, html_template, codingType='utf8'):
        # set mime message with subject, from, to , html template and its encoding type
        self.subject = subject
        msg_obj = MIMEText(html_template, 'html', codingType)
        msg_obj['Subject'] = subject
        msg_obj['from'] = from_
        msg_obj['to'] = to_
        return msg_obj

    def get_username_address(self, email_reciever):
        # according to the email reciever's type, get username, address

        return None, None


    def send_emails_to_recievers(self, from_, email_reciever_list, html, **kwargs):

        while (email_reciever_list):
            # get user name, email address
            email_reciever = email_reciever_list.pop()
            username, addr = self.get_username_address(email_reciever)
            # set html template by substitute key value pairs
            html = self.set_html_template(html, **kwargs)
            # initiate the msg_obj
            msg_obj = self.set_mime_message(self.subject, from_, addr, html)

            try:
                self.server.sendmail(from_, addr, msg_obj.as_string())
                print "send email to {} successfully! ".format(addr)
                time.sleep(2)
            except:
                print "fail to send to %s .. will try it again later..." % username
                self.reconnect_to_server(self.hostname, self.username, self.password)
                # re-insert the email reciever to the sending list
                email_reciever_list.insert(0, email_reciever)
                time.sleep(10)

        print "\nThere are {} emails sent! ".format(len(email_reciever_list))


if __name__ == '__main__':
    host_name = 'smtp.163.com'
    username = 'xxx@163.com'
    password = 'xxxx'
    html_template = ''  # set a template
    email_recievers_list = list()
    kwargs = dict()

    email_sender = EmailSender()
    email_sender.set_smtp_server(host_name)
    email_sender.login_to_server(username, password)
    
    html_template = email_sender.set_html_template(html_template)
    email_sender.send_emails_to_recievers(username,email_recievers_list,html_template,**kwargs)

