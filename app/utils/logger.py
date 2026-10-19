"""Logging setup. On Lambda anything written to stdout/logging goes to
CloudWatch Logs automatically, so we only need a good format + level."""
import logging

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    if root.handlers:  # Lambda already attaches a handler; just restyle it
        for handler in root.handlers:
            handler.setFormatter(formatter)
    else:  # local run
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root.addHandler(handler)
    logging.getLogger("botocore").setLevel(logging.WARNING)
