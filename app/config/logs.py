import logging
from asgi_correlation_id import CorrelationIdFilter


class MissingCorrelationIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'correlation_id') or record.correlation_id is None or record.correlation_id == '':
            record.correlation_id = 'None'
        return True

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
        },
        'custom_formatter': {
            'format': "%(asctime)s - %(name)s:%(lineno)d [%(correlation_id)s] - %(levelname)s - %(message)s"

        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'stream_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'uvicorn': {
            'handlers': ['stream_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['stream_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['stream_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': ['stream_handler'],
            'level': 'TRACE',
            'propagate': False
        },

    },
}


def get_logger(name: str):
    cid_filter = CorrelationIdFilter(uuid_length=32)
    console_handler = logging.StreamHandler()
    console_handler.addFilter(cid_filter)
    console_handler.addFilter(MissingCorrelationIdFilter())
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s:%(lineno)d [%(correlation_id)s] - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', handlers=[console_handler])
    return logging.getLogger(name)


def get_worker_logger(name: str):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    return logging.getLogger(name)