import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTION = 'prd'
STAGING = 'stg'
DEV = 'dev'

LOCAL_SQLALCHEMY_URL = 'sqlite:///' + os.path.join(os.path.dirname(BASEDIR), 'database.db')

common_config = {
    'DEBUG': False,
    'SQLALCHEMY_DATABASE_URI': os.environ.get("SQLALCHEMY_DATABASE_URI", LOCAL_SQLALCHEMY_URL),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'ALLOWED_IMAGES_EXTENSIONS': ['txt'],
    'MAX_IMAGE_SIZE': 16 * 1024 * 1024  # 10MB
}

prd_config = {
    'ENV': PRODUCTION,
    'UPLOAD_TYPE': 's3',
    "S3_BUCKET_NAME": 'img.process.prd'
}

stg_config = {
    'ENV': STAGING,
    "UPLOAD_TYPE": 's3',
    "S3_BUCKET_NAME": 'img.process.stg'
}

dev_config = {
    'ENV': DEV,
    'DEBUG': True,
    'UPLOAD_TYPE': 'lcl',
    'UPLOAD_PATH': os.path.join(BASEDIR, 'uploads'),
}


def get_config():
    env_id = _get_environment()
    return _config_map.get(env_id)


def _get_environment():
    env_var = os.environ.get('ENV')
    if env_var not in [DEV, STAGING, PRODUCTION]:
        return DEV
    return env_var


_config_map = {
    PRODUCTION: {**common_config, **prd_config},
    STAGING: {**common_config, **stg_config},
    DEV: {**common_config, **dev_config},
}
