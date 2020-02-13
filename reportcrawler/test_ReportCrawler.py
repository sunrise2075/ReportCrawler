from reportcrawler.ReportCrawler import ReportCrawler


def test_create_zip_file():
    pass


def test_remove_html_tags():
    html_str = "<em>测试</em>移除html字符串"
    expect_str = "测试移除html字符串"
    assert expect_str == ReportCrawler.remove_html_tags(html_str)
