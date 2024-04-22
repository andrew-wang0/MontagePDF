import pathlib
import platform
import re
import string
from datetime import datetime
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def convert_pdf_to_txt(path: str) -> str:
    resource_manager = PDFResourceManager()
    retstr = StringIO()
    la_params = LAParams()
    device = TextConverter(resource_manager, retstr, laparams=la_params)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, device)
    password = ""
    max_pages = 0
    caching = True
    page_numbers = set()

    for page in PDFPage.get_pages(fp, page_numbers, maxpages=max_pages, password=password, caching=caching,
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


class Performance:
    def __init__(self):
        self.name: str | None = None
        self.instrument: str | None = None
        self.date: str | None = None
        self.location: str | None = None

    def __repr__(self):
        return f'{self.date} - {self.name} - {self.instrument} <{self.location}>'

    def output_heavy(self):
        return f'{self.date}'

    def output_light(self):
        return f' \u2013 {self.name}, {self.instrument}'

    def is_complete(self):
        return all(self.__dict__.values())


class PDFFormatter:
    def __init__(self, pdf_path: str | pathlib.Path):
        self.month = None
        self.performances: list[Performance] | None = None

        text = convert_pdf_to_txt(pdf_path)
        formatted_text = format_pdf_text(text)
        self.formatted_lines_to_performances(formatted_text)

    def performances_for_location(self, location: str):
        return [p for p in self.performances if p.location.lower() == location.lower()]

    def formatted_lines_to_performances(self, lines: list[str]):
        name_instrument_pattern = re.compile(r'(?P<name>.*) - (?P<instrument>.*) \((WeHo|CHOMP)\)')

        time_pattern = re.compile(
            r'(?P<datetime>(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d+/\d+/\d+ \d+:\d+ (AM|PM)) - (\d+:\d+ (AM|PM))')

        location_pattern = re.compile(r'Location:(?P<location>.*)')

        performances = []
        current_performance: Performance = Performance()

        self.month = lines[0].split(' ')[0]

        for line in lines:
            if name_instrument_pattern.match(line):
                d = name_instrument_pattern.match(line).groupdict()
                current_performance.name = d['name']
                current_performance.instrument = d['instrument']

            elif time_pattern.match(line):
                dt = datetime.strptime(time_pattern.match(line).group('datetime'), '%a %m/%d/%Y %I:%M %p')

                if dt.minute == 0:
                    if platform.system() == "Windows":
                        formatted_time = dt.strftime('%A, %B %#d, %#I %p')
                        formatted_time = formatted_time.replace('AM', 'a.m.').replace('PM',
                                                                                      'p.m.')
                    else:
                        formatted_time = dt.strftime('%A, %B %-d, %-I %p')
                        formatted_time = formatted_time.replace('AM', 'a.m.').replace('PM',
                                                                                      'p.m.')
                else:
                    if platform.system() == "Windows":
                        formatted_time = dt.strftime('%A, %B %#d, %#I:%M %p')
                        formatted_time = formatted_time.replace('AM', 'a.m.').replace('PM',
                                                                                      'p.m.')
                    else:
                        formatted_time = dt.strftime('%A, %B %-d, %-I:%M %p')
                        formatted_time = formatted_time.replace('AM', 'a.m.').replace('PM',
                                                                                      'p.m.')

                current_performance.date = formatted_time
            elif location_pattern.match(line):
                loc = location_pattern.match(line).group('location').strip()
                if loc.startswith('CHOMP'):
                    current_performance.location = 'Fountain Court'
                elif loc.startswith('West'):
                    current_performance.location = 'Westland House'
                else:
                    raise ValueError(f'Unknown location: {loc}')

            if current_performance.is_complete():
                performances.append(current_performance)
                current_performance = Performance()

        self.performances = performances
