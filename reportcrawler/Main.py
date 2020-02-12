from reportcrawler.ReportCrawler import ReportCrawler
from reportcrawler.StockCode import StockCode

if __name__ == '__main__':

    stock_code_list = []

    for serial_no in range(2672, 2981):
        stock_code = StockCode(serial_no="00" + str(serial_no), plate="SZ")
        stock_code_list.append(stock_code)

    # with open('stockCode.txt', 'r') as reader:
    #     # Read & print the entire file
    #     text_content = reader.read()
    #     lines = text_content.split('\n')
    #     for line in lines:
    #         serial_no = None
    #         plate = None
    #         if "." in line:
    #             serial_no, plate = line.split('.')
    #             stock_code_list.append(StockCode(serial_no=serial_no, plate=plate))
    #         # elif line.startswith('0'):  # 深市主板
    #         #     serial_no = line
    #         #     plate = "SZ"
    #         #     stock_code_list.append(StockCode(serial_no=serial_no, plate=plate))
    #         elif line.startswith('6'): # 沪市主板
    #             serial_no = line
    #             plate = "SH"
    #             stock_code_list.append(StockCode(serial_no=serial_no, plate=plate))
    #         else:
    #             print("%s的股票代码，不知道是深市还是沪市，无法处理" % line)

    reportCrawler = ReportCrawler(report_file_download_path="http://static.cninfo.com.cn/",
                                  savePath="/Users/sunrise2075/Documents/张翰清博士数据/2018中小企业板企业年报",
                                  input_stock_code=stock_code_list);
    reportCrawler.spy_save()