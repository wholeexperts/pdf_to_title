from pypdf import PdfReader

#该函数的主要作用就是：将pdf转化为text,并且输出前1000个字符。
def pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # print(len(text))
    return text