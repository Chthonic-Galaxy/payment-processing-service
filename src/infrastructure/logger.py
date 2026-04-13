import logging
import logging.config


def setup_logging(level: str | int) -> None:
    """Configure application logging.

    Args:
        level: Root logging level.
    """

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": f"{level}",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": f"{level}",
                "formatter": "default",
                "filename": "/tmp/a_payment_p_s.log",
                "mode": "w",
            },
        },
        "root": {"level": f"{level}", "handlers": ["stdout", "file"]},
    }
    logging.config.dictConfig(config)
