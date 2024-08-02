
class NullLogger:
    def info(self, msg, *args, **kwargs):
        pass  # Do nothing

    def warning(self, msg, *args, **kwargs):
        pass  # Do nothing

    def error(self, msg, *args, **kwargs):
        pass  # Do nothing

    def debug(self, msg, *args, **kwargs):
        pass  # Do nothing

    def critical(self, msg, *args, **kwargs):
        pass  # Do nothing