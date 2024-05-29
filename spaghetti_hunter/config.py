import logging
import logging.config
import pathlib

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')


def setup_logging():
    logs_dir = pathlib.Path.cwd() / 'logs'
    log_conf = {
        'version'                 : 1,
        'disable_existing_loggers': False,
        'formatters'              : {
            'file_form'   : {
                'format': '%(asctime)s - %(levelname)-8s - %(funcName)-22s - %(message)s'
            },
            'console_form': {'format': '%(levelname)-8s - %(message)s'},
        },
        'handlers'                : {
            'console_hand' : {
                'class'    : 'logging.StreamHandler',
                'stream'   : 'ext://sys.stdout',
                'level'    : 'INFO',
                'formatter': 'console_form',
            },
            'file_hand_rot': {
                'class'      : 'logging.handlers.RotatingFileHandler',
                'filename'   : logs_dir / 'spaghetti_hunter.log',
                'maxBytes'   : 3_145_728,  # 3MB
                'backupCount': 5,  # five files with log backup
                'level'      : 'DEBUG',
                'encoding'   : 'utf-8',
                'formatter'  : 'file_form',
            },
            'file_err_hand': {
                'class'      : 'logging.handlers.RotatingFileHandler',
                'filename'   : logs_dir / 'spaghetti_hunter_ERROR.log',
                'maxBytes'   : 3_145_728,  # 3MB
                'backupCount': 5,  # five files with error log backup
                'level'      : 'WARNING',
                'encoding'   : 'utf-8',
                'formatter'  : 'file_form',
            },
        },
        'loggers'                 : {
            '': {
                'handlers': ['console_hand', 'file_hand_rot', 'file_err_hand'],
                'level'   : 'DEBUG',
            },
        },
    }

    # create logs directory
    logs_dir.mkdir(exist_ok=True)
    # setup logging
    logging.config.dictConfig(log_conf)
    logging.debug('logging setup complete')
