import inspect
import logging
import os
import random
import re
import sys
import time
from logging.handlers import TimedRotatingFileHandler

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR + '/../utils')

from read_config import CONFIG


class Logger:

    def __init__(self, logger_name, logger_file, for_testing=False):
        if not for_testing:
            sudopw = CONFIG['machine'].get('sudo_pwd', 'default')
            self.create_log(logger_file, sudopw)
            self.clean_log(logger_file, sudopw)

        formatter = logging.Formatter(
            '[%(asctime)s]:[%(levelname)s] %(message)s'
        )

        file_handler = TimedRotatingFileHandler(
            logger_file, when='H', interval=8, backupCount=21)
        file_handler.suffix = '%Y%m%d_%H:%M:%S'
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        stream_logger = logging.StreamHandler()
        stream_logger.setLevel(logging.INFO)
        stream_logger.setFormatter(formatter)

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_logger)

    @staticmethod
    def __get_call_info():
        try:
            stack = inspect.stack()
        except IndexError:
            return "", "", ""
        fn = os.path.basename(stack[2][1])
        ln = stack[2][2]
        func = stack[2][3]
        return fn, func, ln

    @staticmethod
    def __get_msg(call_info, msg):
        return "[%s:%s:L%s] %s" % (call_info[0], call_info[1], call_info[2], msg)

    def info(self, msg, *args, **kwargs):
        call_info = self.__get_call_info()
        msg = self.__get_msg(call_info, msg)
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        call_info = self.__get_call_info()
        msg = self.__get_msg(call_info, msg)
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        call_info = self.__get_call_info()
        msg = self.__get_msg(call_info, msg)
        self.logger.exception(msg, *args, **kwargs)

    def info_ramdon(self, msg, num=100):
        call_info = self.__get_call_info()
        msg = self.__get_msg(call_info, msg)
        if random.randint(1, num) == 1:
            self.logger.info(msg)


    @staticmethod
    def clean_log(logger_file, sudopw):
        dir_name = os.path.dirname(logger_file)
        file_name = logger_file.split('/')[-1]
        files = os.listdir(dir_name)
        files = [file for file in files if re.findall(file_name + '.', file)]
        files.sort()
        files_size = [os.path.getsize(
            os.path.join(dir_name, file)) for file in files]
        while sum(files_size) > 1024 ** 3:
            earliest_file = os.path.join(dir_name, files[0])
            os.system('echo {}|sudo -S {}'.format(sudopw,
                                                  'rm {}'.format(earliest_file)))
            files.pop(0)
            files_size.pop(0)

    @staticmethod
    def create_log(logger_file, sudopw):
        dir_name = os.path.dirname(logger_file)
        if os.path.exists(dir_name):
            os.system('echo {}|sudo -S {}'.format(sudopw,
                                                  'chmod 777 {}'.format(dir_name)))
        else:
            os.system('echo {}|sudo -S {}'.format(sudopw,
                                                  'mkdir -p -m 777 {}'.format(dir_name)))
        if os.path.exists(logger_file):
            os.system('echo {}|sudo -S {}'.format(sudopw,
                                                  'chmod 777 {}'.format(logger_file)))


def exception_handler(**kwargs):
    def __exception_handler(function):
        def __exception_handler_inner(self, *args):
            name = kwargs.get('name', 'Default Method')
            start = time.time()
            self.logger.info('{}, It Start.'.format(name))
            try:
                function(self, *args)
            except:
                self.logger.exception('{} Failed.'.format(name))
            finally:
                end = time.time()
                self.logger.info(
                    '{}, End. cost: {}s.'.format(name, end - start))

        return __exception_handler_inner

    return __exception_handler


def timer(**kwargs):
    def __timer(function):
        def __timer_inner(self, *args):
            name = kwargs.get('name', 'Default Method')
            start = time.time()
            function(self, *args)
            self.logger.info(f'{name}, End. cost: {time.time() - start}s.')
        return __timer_inner

    return __timer
