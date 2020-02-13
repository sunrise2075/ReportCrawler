import datetime
import logging
import os
import random
import re
import time
import zipfile
from pathlib import Path

import requests


class ReportCrawler:

    def __init__(self, report_file_download_base_path=None,
                 report_list_query_url=None, savePath=None,
                 report_post_query_param_dict=None,
                 stock_code_list=None,
                 report_file_title_whitelist=None,
                 report_file_title_blacklist=None, year=None):
        logging.basicConfig(filename='report_crawler.log', format='%(asctime)s %(message)s', filemode='w',
                            level=logging.INFO)
        self.recsPerPage = 30
        self.report_list_query_path = report_list_query_url
        self.report_file_download_path = report_file_download_base_path or "http://static.cninfo.com.cn/"
        self.report_file_title_whitelist = report_file_title_whitelist or []
        self.report_file_title_blacklist = report_file_title_blacklist or []
        self.savePath = savePath or "./download"
        self.year = year or datetime.datetime.now().year
        self.input_stock_code = stock_code_list or set()
        self.report_post_query_param_dict = report_post_query_param_dict or dict()
        self.http_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                             "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                             "Accept-Encoding": "gzip, deflate",
                             "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5",
                             'Host': 'www.cninfo.com.cn',
                             'Origin': 'http://www.cninfo.com.cn',
                             'Referer': 'http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice',
                             'X-Requested-With': 'XMLHttpRequest'
                             }

        self.http_user_agents = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0"
        ]

    def spy_save(self):
        sub_folder_prefix = self.report_file_title_whitelist[-1]
        rolling_folder_suffix_number = 0

        rolling_file_number = 0
        for stock_code in self.input_stock_code:
            rolling_file_number += 1
            serial_no = stock_code.get_serial_no()
            plate = stock_code.get_plate()

            try:
                announcements = self.single_page_announcement(serial_no, plate)
            except:
                print(stock_code, 'page error, retrying')
                try:
                    announcements = self.single_page_announcement(serial_no, plate)
                except:
                    print(stock_code, 'page error')

            sub_folder_name: str = sub_folder_prefix + "_" + str(rolling_folder_suffix_number)
            self.saving(announcements, stock_code, sub_folder_name)
            if rolling_file_number % 100 == 0:
                # 压缩文件夹
                self.create_zip_file(self.savePath + "//" + sub_folder_name, self.savePath + "//" + sub_folder_name)
                rolling_folder_suffix_number += 1

        # 压缩最后一个文件夹
        sub_folder_name = sub_folder_prefix + str(rolling_folder_suffix_number)
        self.create_zip_file(self.savePath + "//" + sub_folder_name, self.savePath + "//" + sub_folder_name)

    def create_zip_file(self, src_folder, target_file_name):

        file_news = target_file_name + '.zip'  # 压缩后文件夹的名字
        z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
        for dirpath, dirnames, filenames in os.walk(src_folder):
            fpath = dirpath.replace(src_folder, '')  # 这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
            for filename in filenames:
                z.write(os.path.join(dirpath, filename), fpath + filename)
        z.close()

    def single_page_announcement(self, serial_no=None, plate=None):
        self.http_headers['User-Agent'] = random.choice(self.http_user_agents)  # 定义User_Agent
        query = self.report_post_query_param_dict
        query['stock'] = serial_no
        query['pageSize'] = self.recsPerPage
        query['plate'] = plate
        namelist = requests.post(self.report_list_query_path, headers=self.http_headers, data=query)
        return namelist.json()['announcements']  # json中的年度报告信息

    '''
        检查文件名称：
        1. 包含字符: 2018年年度报告 
        2. 满足条件1之后，包含如下任意字符: 更新后 更正版 修订版
        3. 满足条件1和2之后， 不能包含如下全部字符：摘要 英文版 已取消
    '''

    def in_yearly_announcement_title_whitelist(self, announcement_title):

        """
        Check if the given title is in possible_titles
        @precondition: C{announcement_title} is not empty
        """
        assert announcement_title is not None and len(announcement_title) > 0

        for possible_title in self.report_file_title_whitelist:
            if possible_title == announcement_title:
                return True

        return False

    def in_announcement_title_blacklist(self, announcement_title: str) -> bool:

        for possible_title in self.report_file_title_blacklist:
            if possible_title == announcement_title:
                return True

        return False

    def saving(self, announcements, stock_code, sub_folder):
        if len(announcements) == 0:
            logging.warning('当前处理%s的公告，找不到任何年报数据', stock_code)

        for announcement in announcements:

            announcement_title: str = announcement['announcementTitle']
            # 标题中可能会包含html标签
            announcement_title = ReportCrawler.remove_html_tags(announcement_title)
            download_url = self.report_file_download_path + announcement["adjunctUrl"]
            file_name = announcement["secCode"] + '_' + announcement['secName'] + '_' + announcement_title + '.pdf'

            if self.in_yearly_announcement_title_whitelist(announcement_title):
                self.download_file(download_url, sub_folder, file_name, stock_code)
                break
            else:
                # 考虑到按照年份的年报，如果标题没有出现在白名单，也没有出现在黑名单中，我们需要先下载文件，并且提示用户特别关注
                if self.year in announcement_title and not self.in_announcement_title_blacklist(announcement_title):
                    logging.warning("这个公告文件的名字有点特别, 你需要确定自己是否需要这个文件。股票信息: %s, 公告标题: %s，", stock_code,
                                    announcement_title)
                    self.download_file(download_url, sub_folder, file_name, stock_code)

                continue

    @classmethod
    def remove_html_tags(self, file_name_str):
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', file_name_str)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        # s = ReportCrawler.replaceCharEntity(s)  # 替换实体
        return s

    ##替换常用HTML字符实体.
    # 使用正常的字符替换HTML中特殊的字符实体.
    # 你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    # @param htmlstr HTML字符串.
    @classmethod
    def replaceCharEntity(htmlstr: str):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如&gt;
            key = sz.group('name')  # 去除&;后entity,如&gt;为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    @classmethod
    def repalce(s, re_exp, repl_string):
        return re_exp.sub(repl_string, s)

    def download_file(self, download_url, sub_folder, file_name, stock_code):
        if '*' in file_name:
            file_name = file_name.replace('*', '')

        temp_path = self.savePath + '//' + sub_folder
        Path(temp_path).mkdir(parents=True, exist_ok=True)

        file_path = temp_path + '//' + file_name
        time.sleep(random.random() * 5)
        self.http_headers['user-agent'] = random.choice(self.http_user_agents)
        r = requests.get(download_url)
        f = open(file_path, "wb")
        f.write(r.content)
        f.close()
        logging.info('当前处理%s的公告，下载文件路径%s， 生成pdf文件名称%s', stock_code, download_url, file_name)
