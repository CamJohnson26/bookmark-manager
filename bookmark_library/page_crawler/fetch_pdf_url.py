import os
import requests
from io import StringIO
from pdfminer.layout import LAParams

from pdfminer.high_level import extract_text_to_fp
from pdfminer.pdfdocument import PDFEncryptionError
from pdfminer.pdfparser import PDFSyntaxError


def fetch_pdf_url(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    }
    html = requests.get(url, headers=headers, timeout=10).content
    with open('temp.pdf', 'wb') as f:
        f.write(html)
    output_string = StringIO()
    with open('temp.pdf', 'rb') as f:
        try:
            extract_text_to_fp(f, output_string, laparams=LAParams(), output_type='html', codec=None);
        except (
            PDFSyntaxError, PDFEncryptionError
        ):
            print('Could not read this pdf')
    rv = output_string.getvalue().strip()

    os.remove('temp.pdf')
    return rv
