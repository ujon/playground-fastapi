import logging


class ShortenNameFilter(logging.Filter):
    def __init__(self, max_length: int = 30):
        super().__init__()
        self.max_length = max_length

    def filter(self, record: logging.LogRecord) -> bool:
        name = record.name
        if len(name) > self.max_length:
            parts = name.split(".")
            if len(parts) > 1:
                # 마지막 부분 유지, 나머지는 첫 글자만
                shortened = ".".join(p[0] for p in parts[:-1]) + "." + parts[-1]
                record.name = shortened
        return True


# client_api/log_config.py

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "shorten_name": {
            "()": ShortenNameFilter,
            "max_length": 30,
        },
    },
    "formatters": {
        "default": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s%(reset)s\t%(asctime)s\t%(name)-25s\t%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "plain": {
            "format": "%(levelname)s\t%(asctime)s\t%(name)s\t%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["shorten_name"],
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "plain",
            "filters": ["shorten_name"],
            "filename": "app.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "httpx": {
            "level": "ERROR",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "infrastructure.openweather": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        }
    },
}
