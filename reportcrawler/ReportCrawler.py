import datetime
import logging
import os
import random
import time
import zipfile
from pathlib import Path

import requests


class ReportCrawler:

    def __init__(self, report_file_download_path=None, savePath=None, input_stock_code=None, year=None):
        logging.basicConfig(filename='report_crawler.log', format='%(asctime)s %(message)s', filemode='w',
                            level=logging.INFO)
        self.recsPerPage = 30
        self.report_list_query_path = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        self.report_file_download_path = report_file_download_path or "http://static.cninfo.com.cn/"
        self.savePath = savePath or "./download"
        self.year = year or datetime.datetime.now().year
        self.input_stock_code = input_stock_code or set()
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
        sub_folder_prefix = '2018中小企业板企业年报'
        sub_folder_suffix_idx = 7
        index = 0

        for stock_code in self.input_stock_code:
            index += 1
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

            sub_folder_name = sub_folder_prefix + str(sub_folder_suffix_idx)
            self.saving(announcements, stock_code, sub_folder_name)
            if index % 100 == 0:
                # 压缩文件夹
                self.create_zip_file(self.savePath + "//" + sub_folder_name, self.savePath + "//" + sub_folder_name)
                sub_folder_suffix_idx += 1

        # 压缩最后一个文件夹
        sub_folder_name = sub_folder_prefix + str(sub_folder_suffix_idx)
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
        query = {
            'stock': serial_no,
            'tabName': 'fulltext',
            'pageSize': self.recsPerPage,
            'pageNum': 1,
            'column': 'sse',
            'category': 'category_ndbg_szsh;',
            'plate': plate,
            'isHLtitle': 'true'
        }
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

        possible_titles = [
            '2018年年度报告（更新后）',
            '2018年年度报告（更正版）',
            '2018年年度报告（更新版）',
            '2018年年度报告（2019年修订）',
            '2018年年度报告（修订版）',
            '2018年年度报告（更正）',
            '2018年年度报告'
        ]
        for possible_title in possible_titles:
            if possible_title == announcement_title:
                return True

        return False

    def in_announcement_title_blacklist(self, announcement_title: str) -> bool:
        announcement_title_blacklist = [
            'H股公告-2018年年度报告',
            '2018年年度报告（已取消）',
            '2018年年度报告（英文版）',
            '2018年年度报告摘要',
            '2018年年度报告摘要（英文版）',
            '2018年年度报告摘要（修订版）',
            '2018年年度报告摘要（更新后）',
            '2018年年度报告摘要（已取消）',
            '2018年年度报告（印刷版）',
            '2018年年度报告（修订版）',
            '2018年年度报告（修订稿）',
            '2018年年度报告（修订后）',
            '关于公司2018年年度报告修订说明',
            '2018年年度报告摘要',
            '2018年年度报告摘要（更正）',
            '2018年年度报告摘要（修订后）',
            '2018年半年度报告',
            '2018年半年度报告（2019年修订）'
        ]
        for possible_title in announcement_title_blacklist:
            if possible_title == announcement_title:
                return True

        return False

    def saving(self, announcements, stock_code, sub_folder):
        if len(announcements) == 0:
            logging.warning('当前处理%s的公告，找不到任何年报数据', stock_code)

        for announcement in announcements:

            announcement_title: str = announcement['announcementTitle']
            download_url = self.report_file_download_path + announcement["adjunctUrl"]
            file_name = announcement["secCode"] + '_' + announcement['secName'] + '_' + announcement_title + '.pdf'

            if self.in_yearly_announcement_title_whitelist(announcement_title):
                self.download_file(download_url, sub_folder, file_name, stock_code)
                break
            else:
                if '2018' in announcement_title and not self.in_announcement_title_blacklist(announcement_title):
                    logging.warning("这个公告文件的名字有点特别, 你需要确定自己是否需要这个文件。股票信息: %s, 公告标题: %s，", stock_code,
                                    announcement_title)
                    self.download_file(download_url, sub_folder, file_name, stock_code)

                continue

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


