from logging import Formatter
import json


class JsonFormatter(Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *,
                 defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record):
        json_record = {}
        json_record['name'] = record.name
        json_record['asctime'] = self.formatTime(record, self.datefmt)
        json_record['message'] = record.getMessage()
        json_record['level'] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")
        return json.dumps(json_record)
