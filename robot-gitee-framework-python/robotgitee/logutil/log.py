import logging
import json


class _Logger(logging.Logger):
    def __init__(self, name,
                 log_level=logging.DEBUG,
                 log_format=None,
                 data_format=None):
        super().__init__(name, log_level)

        if not log_format:
            log_format = '[%(asctime)s][%(levelname)s]'
            log_format += '[%(filename)s:%(lineno)d]: %(message)s'

        if not data_format:
            data_format = '%Y-%m-%d %H:%M:%S'

        formatter = logging.Formatter(log_format, data_format)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(log_level)

        self.addHandler(console)


class LogUtil(object):
    def __init__(self, logger: _Logger):
        self._logger = logger
        self._fields = dict()

    def field(self, k, v):
        self._fields[k] = v

        return self

    def _get_fields(self) -> str:
        if len(self._fields) > 0:
            return json.dumps(self._fields) + ", "

        return ""

    def info(self, msg, *args, **kwargs):
        if not self._logger:
            return

        s = self._get_fields()
        if s != "":
            self._logger.info(s + msg, *args, **kwargs)
        else:
            self._logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if not self._logger:
            return

        s = self._get_fields()
        if s != "":
            self._logger.error(s + msg, *args, **kwargs)
        else:
            self._logger.error(msg, *args, **kwargs)


_logger = None


def init_logger(name):
    global _logger

    _logger = _Logger(name)


def new_logutil():
    global _logger

    return LogUtil(_logger)

def info(msg, *args, **kwargs):
    global _logger

    if _logger:
        _logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    global _logger

    if _logger:
        _logger.error(msg, *args, **kwargs)
