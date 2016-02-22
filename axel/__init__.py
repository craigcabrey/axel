import configparser
import pushbullet

parser = configparser.ConfigParser()
parser.read('/etc/axel.conf')

config = {}

config['filebot_bin'] = parser.get(
    'General', 'FilebotLocation', fallback='/usr/bin/filebot'
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

pushbullet_client = None
sender = None

if not pushbullet_client and config['pushbullet_key']:
    pushbullet_client = pushbullet.Pushbullet(config['pushbullet_key'])

if config['pushbullet_channel']:
    for channel in pushbullet_client.channels:
        if channel.name == config['pushbullet_channel']:
            sender = channel
    if not sender:
        raise RuntimeError('Could not find specified Pushbullet channel')
else:
    sender = pushbullet_client

prev_message = None
def pb_notify(message):
    global prev_message

    # Prevent spamming runaway messages
    if prev_message == message:
        return

    if sender:
        sender.push_note('Axel', message)
        prev_message = message

from .auditor import audit
from .axel import update_blocklist, handle_finished_download
from .cleaner import clean

del axel
del cleaner
del configparser
del parser
