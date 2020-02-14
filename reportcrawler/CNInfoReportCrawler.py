import logging

from reportcrawler.ReportCrawler import ReportCrawler

'''
巨浪资讯：http://www.cninfo.com.cn/new/index
报告抓取器
'''


class CNInfoReportCrawler(ReportCrawler):

    def __init__(self, report_file_download_base_path=None,
                 report_list_query_url=None, savePath=None,
                 report_post_query_param_dict=None,
                 stock_code_list=None,
                 report_file_title_whitelist=None,
                 report_file_title_blacklist=None, year=None):
        super(CNInfoReportCrawler, self).__init__(report_file_download_base_path=report_file_download_base_path,
                                                  report_list_query_url=report_list_query_url, savePath=savePath,
                                                  report_post_query_param_dict=report_post_query_param_dict,
                                                  stock_code_list=stock_code_list,
                                                  report_file_title_whitelist=report_file_title_whitelist,
                                                  report_file_title_blacklist=report_file_title_blacklist, year=year)

    def save_file(self, report_file_info_item, stock_code, sub_folder):
        if len(report_file_info_item) == 0:
            logging.warning('当前处理%s的公告，找不到任何年报数据', stock_code)

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
