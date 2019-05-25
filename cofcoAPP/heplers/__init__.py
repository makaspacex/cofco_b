#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# Copyright 2017 izhangxm@gmail.com. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
import re
import json
from datetime import datetime
from channels.layers import get_channel_layer
from sys import stdout
import asyncio
# 获得标准时间
def getFTime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Logger(object):
    def __init__(self, fp_locker, file_path, screen_locker):
        self.screen_locker = screen_locker
        self.fp_locker = fp_locker
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        self.fp = open(file_path, 'a+',encoding='utf-8')
        self.channel_layer = get_channel_layer()

    def log(self, tag, user, info, screen=False):
        '''
        日志记录和屏幕输出
        :param user:
        :param tag:
        :param info:
        :return:
        '''
        output_str = "%s %s %s %s" % (getFTime(), tag, user, info)
        try:
            self.fp_locker.acquire()
            self.fp.write(output_str + '\n')
        finally:
            self.fp.flush()
            self.fp_locker.release()

        if screen:
            try:
                self.screen_locker.acquire()
                output_str = "\033[0;31m%s %s %s %s\033[0m" % (getFTime(), tag, user, info)
                if tag == 'INFO':
                    output_str = '\033[0;32m%s %s %s %s\033[0m'% (getFTime(), tag, user, info)
                loop = asyncio.get_event_loop()
                coroutine = get_channel_layer().group_send('group_view_spider_log', {'type': 'log_message', 'message': output_str})
                loop.run_until_complete(coroutine)
                print(output_str)
            finally:
                stdout.flush()
                self.screen_locker.release()

def parse_raw_cookies(raw_cookies):
    try:
        # 解析raw_cookies为标准格式
        raw_cookies = re.sub(r'\s', '', raw_cookies).split(';')
        cookies = {}
        for ele in raw_cookies:
            key, value = ele.split('=')
            cookies[key] = value
        cookies = json.loads(json.dumps(cookies))
        return cookies
    except Exception:
        raise Exception('Parse the raw cookies failed!')


# 检查用户输入的cookie是否有效，有效的话返回登录的用户名
def check_cookies_valid(sessionHelper):
    rsp= sessionHelper.get('https://www.fenqubiao.com/Core/CategoryList.aspx')
    if rsp.status_code == 200:
        r = re.search(r'<li><a href="../Core/ToDefault.ashx[\s\S]*?>([\S]+)[\s\S]+?</li>',rsp.text)
        if r:
            return r.group(1)
        return False
    raise Exception('Check_cookies_valid Connection Error')