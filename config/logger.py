import logging.config
from pathlib import Path

log_dir = Path("log")
log_file = log_dir / "logfile.log"
log_dir.mkdir(parents=True, exist_ok=True)

logger_config_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'std_format': {
            'format': '{asctime} {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        },
        'logfile': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': log_file,
            'encoding': 'utf-8',
            'mode': 'a',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'logger': {
            'level': 'DEBUG',
            'handlers': ['console', 'logfile'],
            # 'propagate': False
        }
    },
    'filters': {},
    'root': {}
}

logging.config.dictConfig(logger_config_dict)
logger = logging.getLogger('logger')
