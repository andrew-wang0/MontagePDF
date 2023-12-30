class Performance:
    def __init__(self):
        self.name = None
        self.instrument = None
        self.date = None
        self.location = None

    def __repr__(self):
        # Saturday, September 2, 1 p.m. – Tamas Marius, Flute
        return f'{self.date} - {self.name} - {self.instrument} <{self.location}>'

    def output_string(self):
        return f'{self.date} - {self.name} - {self.instrument}'

    def is_complete(self):
        return (self.name is not None and
                self.instrument is not None and
                self.date is not None and
                self.location is not None)
