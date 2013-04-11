import collections


class YunoError(Exception):
    @classmethod
    def from_exception(cls, e):
        return cls(str(e))


    def __init__(self, message):
        self.message = message


    def for_console(self):
        return '\n{}\n'.format(
            ''.join(['!   ' + line for line in self.message.splitlines(True)])
        )


    def __str__(self):
        return self.message


class SuiteLoadError(YunoError):
    def __init__(self, name):
        message = 'Could not load suite %s (%s)' % (name, name)
        super(SuiteLoadError, self).__init__(message)


class SuiteSaveError(YunoError):
    def __init__(self, name, filename):
        message = 'Could not save suite %s (%s)' % (name, filename)
        super(SuiteSaveError, self).__init__(message)


class EmptyTestSet(YunoError):
    def __init__(self, message='No tests to run'):
        super(EmptyTestSet, self).__init__(message)


class ConfigLoadError(YunoError):
    def __init__(self, filename):
        super(ConfigLoadError, self).__init__(
            'Could not read config file: ' + filename
        )


class ConfigParseError(YunoError):
    def __init__(self, filename):
        super(ConfigParseError, self).__init__(
            'Error parsing a config file: ' + filename
        )


class UndefinedConfigKey(YunoError):
    def __init__(self, key_name):
        super(UndefinedConfigKey, self).__init__(
            'Key {} does not exist in the settings.'.format(key_name)
        )


class DataFileError(YunoError):
    message_wrapper = 'Operation failed on a data file.\nPython said: '

    def __init__(self, message, use_raw=False):
        if not use_raw:
            message = DataFileError.message_wrapper + message

        super(DataFileError, self).__init__(message)


class converted(object):
    def __init__(self, from_types, to=None):
        self._convert_to = to
        self._convert_from = from_types


    def __enter__(self):
        pass


    def __exit__(self, type, value, error):
        if isinstance(value, self._convert_from):
            raise self._convert_to.from_exception(value)
            return True
