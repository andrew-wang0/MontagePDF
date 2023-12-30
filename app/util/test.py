import re
import string
from datetime import datetime
from io import StringIO

from app.util.performance import Performance
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def convert_pdf_to_txt(path: str) -> str:
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def format_pdf_text(text: str) -> list[str]:
    res = ''.join(filter(lambda x: x in string.printable, text))
    res = [line.strip() for line in res.split('\n') if line.strip() != '']

    final = []
    for line in res:
        if final and final[-1] == line:
            continue
        else:
            final.append(line)

    return res


def main():
    text = convert_pdf_to_txt(r"/app\files\calendar.pdf")
    res = format_pdf_text(text)

    name_instrument_pattern = re.compile(r'(?P<name>.*) - (?P<instrument>.*) \((WeHo|CHOMP)\)')
    time_pattern = re.compile(
        r'(?P<datetime>(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d+/\d+/\d+ \d+:\d+ (AM|PM)) - (\d+:\d+ (AM|PM))')
    location_pattern = re.compile(r'Location:(?P<location>.*)')

    performances = []
    current_performance: Performance = Performance()

    for line in res:
        if current_performance.is_complete():
            performances.append(current_performance)
            current_performance = Performance()

        if name_instrument_pattern.match(line):
            d = name_instrument_pattern.match(line).groupdict()
            current_performance.name = d['name']
            current_performance.instrument = d['instrument']

        elif time_pattern.match(line):
            dt = datetime.strptime(time_pattern.match(line).group('datetime'), '%a %m/%d/%Y %I:%M %p')
            current_performance.date = dt.strftime('%A, %B %d, %Y %I %p')
        elif location_pattern.match(line):
            loc = location_pattern.match(line).group('location').strip()
            if loc.startswith('CHOMP'):
                current_performance.location = 'Fountain Court'
            elif loc.startswith('West'):
                current_performance.location = 'Westland House'

    print(performances)

main()
