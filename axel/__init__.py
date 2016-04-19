import configparser
import shutil

parser = configparser.ConfigParser()
parser.read('/etc/axel.conf')

config = {}

config['filebot_bin'] = parser.get(
    'General', 'FilebotLocation', fallback=lambda: shutil.which('filebot')
)
config['mediainfo_bin'] = parser.get(
    'General', 'MediaInfoLocation', fallback=lambda: shutil.which('mediainfo')
)
config['pushbullet_key'] = parser.get(
    'General', 'PushbulletKey', fallback=''
)
config['pushbullet_channel'] = parser.get(
    'General', 'PushbulletChannel', fallback=''
)
config['movie_dir'] = parser.get(
    'General', 'MovieDirectory'
)
config['tv_dir'] = parser.get(
    'General', 'TVDirectory'
)
config['tmdb_api_key'] = parser.get(
    'General', 'TheMovieDBAPIKey', fallback=''
)

config['transmission'] = {}
config['transmission']['host'] = parser.get(
    'Transmission', 'Host', fallback='localhost'
)
config['transmission']['port'] = parser.get(
    'Transmission', 'Port', fallback=9091
)
config['transmission']['user'] = parser.get(
    'Transmission', 'User', fallback=''
)
config['transmission']['password'] = parser.get(
    'Transmission', 'Password', fallback=''
)
config['transmission']['whitelist'] = parser.get(
    'Transmission', 'Whitelist', fallback=''
).split(',')
config['transmission']['time_threshold'] = int(parser.get(
    'Transmission', 'TimeThreshold', fallback=14
))
config['transmission']['ratio_threshold'] = int(parser.get(
    'Transmission', 'RatioThreshold', fallback=2
))

config['couchpotato'] = {}
config['couchpotato']['category'] = parser.get(
    'CouchPotato', 'Category', fallback='couchpotato'
)
config['couchpotato']['ignore'] = parser.getboolean('CouchPotato', 'Ignore')

config['sonarr'] = {}
config['sonarr']['category'] = parser.get(
    'Sonarr', 'Category', fallback='sonarr'
)
config['sonarr']['ignore'] = parser.getboolean('Sonarr', 'Ignore')
config['sonarr']['drone_factory'] = parser.get('Sonarr', 'DroneFactory')

from .auditor import audit
from .cleaner import clean
from .core import update_blocklist, handle_finished_download

del auditor
del cleaner
del configparser
del core
del parser
del shutil
