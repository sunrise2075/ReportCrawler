import yaml

from reportcrawler.CNInfoReportCrawler import CNInfoReportCrawler
from reportcrawler.ReportCrawler import ReportCrawler
from reportcrawler.StockCode import StockCode

if __name__ == '__main__':

    stock_code_list = []

    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        report_file_download_base_path = cfg['report']['file']['download']['baseUrl']
        report_file_save_path = cfg['report']['file']['savePath']
        report_file_list_query_url = cfg['report']['file']['list']['queryUrl']
        report_file_title_whitelist = cfg['report']['file']['title']['whiteList']
        report_file_title_blacklist = cfg['report']['file']['title']['blackList']
        report_post_query_param_dict = cfg['report']['file']['post']['query']
        code_str_len = cfg['stock']['code']['strLength']
        code_range_from = cfg['stock']['code']['range']['from']
        code_range_to = cfg['stock']['code']['range']['to']
        code_range_plate = cfg['stock']['code']['range']['plate']
        code_file_path = cfg['stock']['code']['filePath']

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

    reportCrawler: ReportCrawler = CNInfoReportCrawler(report_file_download_base_path=report_file_download_base_path,
                                                       report_list_query_url=report_file_list_query_url,
                                                       report_post_query_param_dict=report_post_query_param_dict,
                                                       report_file_title_whitelist=report_file_title_whitelist,
                                                       report_file_title_blacklist=report_file_title_blacklist,
                                                       savePath=report_file_save_path,
                                                       stock_code_list=stock_code_list, year='2018');
    reportCrawler.spy_save()
