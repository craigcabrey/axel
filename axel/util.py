import pushbullet

from axel import config

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


def check_extension(filename):
    return any(filename.endswith(ext) for ext in config['media_file_extensions'])

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message, level='info'):
    if level == 'info':
        print('{bold}==>{end} {message}'.format(
            message=message,
            bold=Colors.BOLD,
            end=Colors.END
        ))
    elif level == 'warn':
        print('{bold}==>{end} {warn}WARNING{end}: {message}'.format(
            message=message,
            bold=Colors.BOLD,
            warn=Colors.WARNING,
            end=Colors.END
        ))
    elif level == 'error':
        print('{bold}==>{end} {error}ERROR{end}: {message}'.format(
            message=message,
            bold=Colors.BOLD,
            error=Colors.FAIL,
            end=Colors.END
        ))
