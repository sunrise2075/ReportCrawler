# Background

This web crawler is built to download pdf report in batch from `http://www.cninfo.com.cn/new/index`.

I had spent about 2 weeks on this simple web crawler in response to the need of a amateur economist one of my close friends in `Shenzhen`.
He told me that it's very labour intensive to download each report manually. So I built this tool. He had borrowed some money from me and didn't pay back so I realised that he is a fake economist. We are no friends since that. But the tool is still useful.

I had employed the features of object oriented design in Python. I leaned some very important things aboutn this language.

# Structure

## `reports` folder

PDF files will be downloaded to to this directory.

## `stockCode.txt` file

You guys can add stock code of `Shanghai Stock Exchange`. The crawler will check each code and try to download annual report of that company from target website.

## `test_ReportCrawler.py`

It's a file filled with unit test case while I wrote this program.