#!/usr/bin/env python
# -*- encoding=utf8 -*-
import datetime
import traceback
from urllib.parse import quote

import requests
import smtplib

from .config import global_config
from .jd_logger import logger

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class Email():
    def __init__(self, mail_user, mail_pwd, mail_host='', mail_receiver=''):
        if global_config.getRaw('messenger', 'email_enable') == 'false':
            return
        if mail_receiver != '':
            self.mail_receiver = mail_receiver
        else:
            self.mail_receiver = mail_user


        smtpObj = smtplib.SMTP()
        # 没传会自动判断 判断不出来默认QQ邮箱
        if mail_host:
            self.mail_host = mail_host
        elif mail_user.endswith('163.com'):
            self.mail_host = 'smtp.163.com'
        elif mail_user.endswith(('sina.com', 'sina.cn')):
            self.mail_host = 'smtp.163.com'
        elif mail_user.endswith('qq.com'):
            self.mail_host = 'smtp.qq.com'
        elif mail_user.endswith('sohu.com'):
            self.mail_host = 'smtp.sohu.com'
        else:
            self.mail_host = 'smtp.qq.com'
        self.mail_user = mail_user
        self.is_login = False
        try:
            smtpObj.connect(mail_host, 25)
            smtpObj.login(mail_user, mail_pwd)
            self.is_login = True
        except Exception as e:
            logger.info('邮箱登录失败!', e)
        self.smtpObj = smtpObj

    def send(self, title, msg, receivers: list, img=''):
        """
        发送smtp邮件至收件人
        :param title:
        :param msg: 如果发送图片，需在msg内嵌入<img src='cid:xxx'>，xxx为图片名
        :param receivers:
        :param img: 图片名
        :return:
        """
        if self.is_login:
            message = MIMEMultipart('alternative')
            msg_html = MIMEText(msg, 'html', 'utf-8')
            message.attach(msg_html)
            message['Subject'] = title
            message['From'] = self.mail_user
            if img:
                with open(img, "rb") as f:
                    msg_img = MIMEImage(f.read())
                msg_img.add_header('Content-ID', img)
                message.attach(msg_img)
            try:
                self.smtpObj.sendmail(self.mail_user, receivers, message.as_string())
            except Exception as e:
                logger.info('邮件发送失败!', e)
        else:
            logger.info('邮箱未登录')


email = Email(
    mail_host=global_config.getRaw('messenger', 'email_host'),
    mail_user=global_config.getRaw('messenger', 'email_user'),
    mail_pwd=global_config.getRaw('messenger', 'email_pwd'),
    mail_receiver=global_config.getRaw('messenger', 'email_user_receiver'),
)


class Messenger(object):
    """消息推送类"""

    def send(self, title='标题', desp='内容....'):
        if not title.strip():
            logger.error('Text of message is empty!')
            return

        now_time = str(datetime.datetime.now())
        content = '[{0}]'.format(now_time) if not desp else '{0} [{1}]'.format(desp, now_time)
        try:
            self._send_sc(title, content)
            self._send_bark(title, content)
            self._send_email(title, content)
        except requests.exceptions.RequestException as req_error:
            logger.error('Request error: %s', req_error)
            traceback.print_exc()
        except Exception as e:
            logger.error('Fail to send message [text: %s, desp: %s]: %s', title, desp, e)
            traceback.print_exc()

    def send_email(self, title, msg, receivers: list, img=''):
        email.send(title, msg, receivers, img)

    def _send_sc(self, title, content):
        """推送信息到微信"""
        if global_config.getRaw('messenger', 'server_chan_enable') == 'true':
            logger.info('推送信息到微信')
            url = 'http://sc.ftqq.com/{}.send'.format(global_config.getRaw('messenger', 'server_chan_sckey'))
            payload = {
                "text": title,
                "desp": content
            }
            headers = {
                'User-Agent': global_config.get('config', 'DEFAULT_USER_AGENT')
            }
            requests.get(url, params=payload, headers=headers)

    def _send_bark(self, title, content):
        """推送信息到bark"""
        if global_config.getRaw('messenger', 'bark_enable') == 'true':
            logger.info('推送信息到bark')
            url = '{}/{}/{}'.format(global_config.getRaw('messenger', 'bark_push'), title,
                                    quote(content, 'utf-8'))
            headers = {
                'User-Agent': global_config.getRaw('config', 'DEFAULT_USER_AGENT')
            }
            requests.get(url, headers=headers)

    def _send_email(self, title, content):
        if global_config.getRaw('messenger', 'email_enable') == 'true':
            logger.info('推送信息到邮箱')
            email.send(title, content, [email.mail_receiver])
