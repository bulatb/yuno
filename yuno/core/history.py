import posixpath
import re

from datetime import datetime

from yuno.core import errors, util
from yuno.core.config import config


class RunRecord(object):
    _fields = ['regressions', 'fixes', 'passed', 'failed', 'skipped', 'warned']
    _line_types = {
        '-': 'regressions',
        '+': 'fixes',
        'p': 'passed',
        'f': 'failed',
        'w': 'warned',
        's': 'skipped',
    }

    # _line_types + _line_labels = fake bimap
    _line_labels = {v: k for k, v in _line_types.items()}
    _header_line = '= Last run [%s] (-%d +%d p%d f%d s%d w%d)\n\n'
    time_format = '%I:%M %p %b %d'

    @classmethod
    def from_last_run(cls):
        return RunRecord.from_file(
            posixpath.join(config.data_folder, 'last-run.txt'))


    @classmethod
    def from_file(cls, path):
        with errors.converted((IOError, TypeError), to=errors.DataFileError):
            fields = {field: [] for field in RunRecord._fields}
            run_time = None

            with open(path) as record:
                for line in record:
                    line_type = RunRecord._line_types.get(line[0])

                    if line_type in fields:
                        fields[line_type].append(
                            util.strip_line_labels(line).strip()
                        )
                    elif line.startswith('='):
                        run_time = re.search(r'\[(.*)\]', line).group(1)

            timestamp = datetime.strptime(run_time, RunRecord.time_format)
            return RunRecord(when=timestamp, **fields)


    def __init__(self, when=None, **kwargs):
        for metric in RunRecord._fields:
            self.__dict__[metric] = kwargs.get(metric) or []

        self.when = datetime.now() if when is None else when


    def save(self, filename=None):
        if filename is None:
            filename = posixpath.join(config.data_folder, 'last-run.txt')

        def save_field(field_name, fp):
            tests = self.__dict__[field_name]
            header = '%d %s\n' % (len(tests), field_name)
            label = RunRecord._line_labels[field_name]

            fp.write(header)
            fp.write('\n'.join([label + ' ' + str(test) for test in tests]))
            fp.write('\n' + ('.' * 80) + '\n')


        with open(filename, 'w+') as record_file:
            record_file.write(RunRecord._header_line % (
                (self.when or datetime.now()).strftime(RunRecord.time_format),
                len(self.regressions), len(self.fixes),
                len(self.passed), len(self.failed),
                len(self.skipped), len(self.warned)
            ))

            for field in RunRecord._fields:
                save_field(field, record_file)
