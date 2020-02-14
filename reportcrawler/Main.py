import yaml

from reportcrawler.CNInfoReportCrawler import CNInfoReportCrawler
from reportcrawler.ReportCrawler import ReportCrawler
from reportcrawler.StockCode import StockCode

if __name__ == '__main__':
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        options: dict = cfg['cninfo']

        reportCrawler: ReportCrawler = CNInfoReportCrawler(options=options);
        reportCrawler.spy_save()
