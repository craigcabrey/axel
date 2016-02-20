import configparser

parser = configparser.ConfigParser()
parser.read('/etc/axel.conf')

config = {}

config['filebot_bin'] = parser.get(
    'General', 'FilebotLocation', fallback='/usr/bin/filebot'
)
config['pushbullet_key'] = parser.get(
    'General', 'PushbulletKey', fallback=''
)
config['movie_dir'] = parser.get(
    'General', 'MovieDirectory'
)
config['tv_dir'] = parser.get(
    'General', 'TVDirectory'
)

config['transmission'] = {}
config['transmission']['host'] = parser.get(
    'Transmission', 'Host', fallback='localhost'
)
config['transmission']['port'] = parser.get(
    'Transmission', 'Port', fallback=9091
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

from .axel import update_blocklist, handle_finished_download
from .cleaner import clean

del axel
del cleaner
del configparser
del parser
