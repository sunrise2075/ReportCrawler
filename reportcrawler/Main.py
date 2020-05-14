import yaml

from reportcrawler.CNInfoReportCrawler import CNInfoReportCrawler
from reportcrawler.ReportCrawler import ReportCrawler

if __name__ == '__main__':
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        options: dict = cfg['cninfo']

        reportCrawler: ReportCrawler = CNInfoReportCrawler(options=options)
        reportCrawler.spy_save()

        # https://www.cnblogs.com/gl1573/p/10064438.html
    # pdf_path = "./reports/000001_平安银行_2018年年度报告.pdf"
    # pdf_reader = ReportReader(file_path=pdf_path)
    # print(pdf_reader.get_fulltext())
