#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import colorlog
import argparse
import importlib
from pathlib import Path
from io import TextIOWrapper
from datetime import datetime


def prepare(app, description, verbosity):
    return CommandLineInterface(app=app,
                                description=description,
                                verbosity=verbosity)


def add_subcommands(subcmd_modules, parser):
    subparsers = parser.add_subparsers(dest='subcommand')
    for module in subcmd_modules:
        subcommand = subparsers.add_parser(
            name=module.__name__.split('.')[-1],
            help=module.__doc__ or '',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        module.cli(subcommand)


class CommandLineInterface(object):
    def __init__(self, app, description, verbosity):
        self.app = app
        self.description = description

        self.start_time = datetime.now()

        self.arguments = self.read_cli_arguments(description, verbosity)
        self.log = logging.getLogger(app)

    def read_cli_arguments(self, description, verbosity):
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            default=verbosity,
                            help='verbose output')

        subparsers = parser.add_subparsers(dest='subcommand')
        for module in self.load_subcommands():
            subcommand = subparsers.add_parser(
                name=module.__name__.split('.')[-1],
                help=module.__doc__ or '',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
            module.cli(subcommand)

        # parser.set_default_subparser(name=config.defaults.subcommand)

        args = parser.parse_args()
        return args

    def load_subcommands(self):
        subcommand_directory = Path('.') / self.app / 'commands'
        for subcommand_module_file in subcommand_directory.glob('*.py'):
            subcommand_module_filename = subcommand_module_file.name
            if subcommand_module_filename.startswith('__'):
                continue

            subcommand_module_name = subcommand_module_filename.replace('.py', '')

            subcommand_package = f'{self.app}.commands.{subcommand_module_name}'
            yield importlib.import_module(name=subcommand_package)

    def __enter__(self):
        self.setup_logger()

        # figure out which argument key is the longest so that all the
        # parameters can be printed out nicely
        self.log.debug('Command-line arguments:')
        length_of_longest_key = len(max(vars(self.arguments).keys(),
                                        key=lambda k: len(k)))
        for arg in vars(self.arguments):
            value = getattr(self.arguments, arg)
            if callable(value):
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value='{}.{}()'.format(value.__module__, value.__name__)
                ))

            elif isinstance(value, TextIOWrapper):
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value=value.name))

            else:
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value=value))

        self.log.debug(self.start_time)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type in (KeyboardInterrupt, SystemExit):
            return False

        elif exc_type is not None:
            self.log.exception("Something happened and I don't know "
                               "what to do")
            return False

        else:
            finish_time = datetime.now()
            self.log.debug(finish_time)
            self.log.debug('Execution time: {time}'.format(
                time=(finish_time - self.start_time)
            ))
            self.log.debug("#" * 20 + " END EXECUTION " + "#" * 20)
            return True

    def setup_logger(self):
        self.log = logging.getLogger(self.app)
        self.log.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        log_file = os.path.join('/tmp', self.app + '.log')
        in_dev_debug_file_handler = logging.FileHandler(
            os.path.join('/tmp', '{}.development.log'.format(self.app))
        )
        in_dev_debug_file_handler.setLevel(logging.DEBUG)

        readable_debug_file_handler = logging.FileHandler(
            os.path.join('/tmp', '{}.debug.log'.format(self.app))
        )
        readable_debug_file_handler.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        command_line_logging = logging.StreamHandler()

        if self.arguments.verbose:
            command_line_logging.setLevel(logging.DEBUG)

            # add relpathname log format attribute so as to only show the file
            #  in which a log was initiated, relative to the project path
            #  e.g. pathname = /full/path/to/project/package/module.py
            #       relpathname = package/module.py
            default_record_factory = logging.getLogRecordFactory()
            project_path = os.path.dirname(os.path.abspath(sys.argv[0])) + \
                           os.sep
            def relpathname_record_factory(*args, **kwargs):
                record = default_record_factory(*args, **kwargs)
                record.relpathname = record.pathname.replace(project_path, '')
                return record
            logging.setLogRecordFactory(relpathname_record_factory)

            # add colors to the logs!
            colored_files_funcs_linenos_formatter = colorlog.ColoredFormatter(
                fmt=(
                    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s"
                    " [ %(relpathname)s::%(funcName)s():%(lineno)s ] "
                    "%(message)s"
                ),
                datefmt='%Y-%m-%d %H:%M:%S',
                reset=True,
            )
            in_dev_debug_file_handler.setFormatter(
                colored_files_funcs_linenos_formatter)
            command_line_logging.setFormatter(
                colored_files_funcs_linenos_formatter)

        else:
            command_line_logging.setLevel(logging.INFO)

        # add the handlers to the logger
        self.log.addHandler(in_dev_debug_file_handler)
        self.log.addHandler(command_line_logging)
        self.log.addHandler(readable_debug_file_handler)
