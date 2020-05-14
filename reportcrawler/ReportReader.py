import pdfplumber


def extract_tables_in_page(page):
    for pdf_table in page.extract_tables():
        table = []
        cells = []
        for row in pdf_table:
            if not any(row):
                # 如果一行全为空，则视为一条记录结束
                if any(cells):
                    table.append(cells)
                    cells = []
            elif all(row):
                # 如果一行全不为空，则本条为新行，上一条结束
                if any(cells):
                    table.append(cells)
                    cells = []
                table.append(row)
            else:
                if len(cells) == 0:
                    cells = row
                else:
                    for i in range(len(row)):
                        if row[i] is not None:
                            cells[i] = row[i] if cells[i] is None else cells[i] + row[i]

        return table
    # for row in table:
    #     print([re.sub('\s+', '', cell) if cell is not None else None for cell in row])
    # print('---------- 分割线 ----------')


class ReportReader:
    def __init__(self, file_path: str = None):
        if file_path:
            try:
                self.file_path = file_path
                with pdfplumber.open(file_path) as pdf:
                    self.pdf_obj = pdf
                    self.meta_data = self.pdf_obj.metadata
                    self.full_text = self.extract_text()
                    # self.all_tables = self.extract_table()
                    pdf.close()
            except:
                raise EnvironmentError("文件路径{}无效，请检查输入的文件路径".format(self.file_path))
        else:
            raise EnvironmentError("文件路径{}无效，请检查输入的文件路径".format(self.file_path))

    def extract_text(self):
        text = ""
        for page in self.pdf_obj.pages:
            text += page.extract_text()

        return text

    # def extract_table(self):
    #     table_result = []
    #     for page in self.pdf_obj:
    #         tables_of_curr_page = self.extract_tables_in_page(page)
    #         table_result.append(tables_of_curr_page)
    #
    #     return table_result

    def get_fulltext(self):
        return self.full_text

    # def get_all_tables(self):
    #     return self.all_tables
