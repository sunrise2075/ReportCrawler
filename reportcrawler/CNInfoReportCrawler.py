import logging

from reportcrawler.ReportCrawler import ReportCrawler
from reportcrawler.StockCode import StockCode

'''
巨浪资讯：http://www.cninfo.com.cn/new/index
报告抓取器
'''


class CNInfoReportCrawler(ReportCrawler):

    def __init__(self, options:dict=None):
        report_file_download_base_path = options['report']['file']['download']['baseUrl']
        report_file_save_path = options['report']['file']['savePath']
        report_file_list_query_url = options['report']['file']['list']['queryUrl']
        report_file_title_whitelist = options['report']['file']['title']['whiteList']
        report_file_title_blacklist = options['report']['file']['title']['blackList']
        report_post_query_param_dict = options['report']['file']['post']['query']
        code_str_len = options['stock']['code']['strLength']
        code_range_from = options['stock']['code']['range']['from']
        code_range_to = options['stock']['code']['range']['to']
        code_range_plate = options['stock']['code']['range']['plate']
        code_file_path = options['stock']['code']['filePath']

        stock_code_list = []
        for serial_no in range(code_range_from, code_range_to + 1):
            stock_code = StockCode(serial_no=str(serial_no).zfill(code_str_len), plate=code_range_plate)
            stock_code_list.append(stock_code)

        # with open(code_file_path, 'r') as reader:
        #     # Read & print the entire file
        #     text_content = reader.read()
        #     lines = text_content.split('\n')
        #     for line in lines:
        #         serial_no = None
        #         plate = None
        #         if "." in line:
        #             serial_no, plate = line.split('.')
        #             stock_code_list.append(StockCode(serial_no=serial_no, plate=plate))
        #         else:
        #             print("%s的股票代码，不知道是深市还是沪市，无法处理" % line)

        super(CNInfoReportCrawler, self).__init__(report_file_download_base_path=report_file_download_base_path,
                                                  report_list_query_url=report_file_list_query_url, savePath=report_file_save_path,
                                                  report_post_query_param_dict=report_post_query_param_dict,
                                                  stock_code_list=stock_code_list,
                                                  report_file_title_whitelist=report_file_title_whitelist,
                                                  report_file_title_blacklist=report_file_title_blacklist, year='2018')

    def save_file(self, report_file_info_item, stock_code, sub_folder):
        if len(report_file_info_item) == 0:
            logging.warning('当前处理%s的公告，找不到任何年报数据', stock_code)
            return

        for announcement in report_file_info_item:

            announcement_title: str = announcement['announcementTitle']
            # 标题中可能会包含html标签
            announcement_title = ReportCrawler.remove_html_tags(announcement_title)
            download_url = self.report_file_download_path + announcement["adjunctUrl"]
            file_name = announcement["secCode"] + '_' + announcement['secName'] + '_' + announcement_title + '.pdf'

            if self.is_in_title_whitelist(announcement_title):
                self.download_file(download_url, sub_folder, file_name, stock_code)
                break
            else:
                # 考虑到按照年份的年报，如果标题没有出现在白名单，也没有出现在黑名单中，我们需要先下载文件，并且提示用户特别关注
                if self.year in announcement_title and not self.is_in_title_blacklist(announcement_title):
                    logging.warning("这个公告文件的名字有点特别, 你需要确定自己是否需要这个文件。股票信息: %s, 公告标题: %s，", stock_code,
                                    announcement_title)
                    self.download_file(download_url, sub_folder, file_name, stock_code)

                continue
