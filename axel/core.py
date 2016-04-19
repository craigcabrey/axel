import guessit
import os
import re
import shutil
import subprocess
import sys
import syslog
import tempfile
import textwrap
import transmissionrpc
import unrar.rarfile
import unrar.unrarlib

from axel import config
from axel.util import pb_notify
from axel.util import check_extension

filebot_bin = config['filebot_bin']
movie_dir = config['movie_dir']
tv_dir = config['tv_dir']

transmission_host = config['transmission']['host']
transmission_port = config['transmission']['port']
transmission_user = config['transmission']['user']
transmission_password = config['transmission']['password']
whitelist = config['transmission']['whitelist']

couchpotato_category = config['couchpotato']['category']
ignore_couchpotato = config['couchpotato']['ignore']

sonarr_category = config['sonarr']['category']
ignore_sonarr = config['sonarr']['ignore']
drone_factory = config['sonarr']['drone_factory']


def whitelisted(torrent):
    return any(
        host in tracker['announce']
            for host in whitelist
                for tracker in torrent.trackers
    )


def update_blocklist():
    transmission_client = transmissionrpc.Client(
        transmission_host, port=transmission_port, user=transmission_user,
        password=transmission_password
    )
    transmission_client.blocklist_update()


def extract(path, destination):
    if unrar.rarfile.is_rarfile(path):
        try:
            rar = unrar.rarfile.RarFile(path)
            if not rar.testrar():
                # Use a set to prevent duplicates from infolist()
                paths = set()
                for member in rar.infolist():
                    if check_extension(member.filename):
                        paths.add(rar.extract(member, path=destination))

                pb_notify(
                    'Successfully unpacked rar archive: {0}'.format(file_path)
                )

                return paths
            else:
                pb_notify('{0} failed the rar integrity check'.format(path))
        except unrar.unrarlib.UnrarException:
            pb_notify('Error while opening {0}'.format(path))
    pb_notify('Failed to unpacked rar archive (not a rar): {0}'.format(path))
    return False


def move_movie(path, guess, move=True):
    required_keys = ('title', 'year', 'screen_size', 'container')
    if all(key in guess for key in required_keys):
        dir_name = '{0} ({1})'.format(guess['title'], guess['year'])
        movie_dir_path = os.path.join(movie_dir, dir_name)

        if not os.path.exists(movie_dir_path):
            os.mkdir(movie_dir_path)

        destination_path = os.path.join(
            movie_dir_path,
            '{title} ({year}) - {size}.{container}'.format(
                title=guess['title'],
                year=guess['year'],
                size=guess['screen_size'],
                container=guess['container']
            )
        )

        if move:
            shutil.move(path, destination_path)
        else:
            shutil.copyfile(path, destination_path)
    else:
        action = 'move' if move else 'copy'

        command = [
            filebot_bin,
            '--action',
            action,
            '--db',
            'TheMovieDB',
            '--format',
            '{n} ({y})/{n} ({y}) - {vf}',
            '-non-strict',
            '-unixfs',
            '-rename',
            path,
            '--output',
            movie_dir
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE)

        if result.returncode != 0:
            pb_notify('Failed to rename {0} using filebot'.format(path))
        elif b'Skipped' in result.stdout and b'already exists' in result.stdout:
            pb_notify('Filebot skipped {0}: already exists'.format(path))


def move_episode(path, guess, move=True):
    required_keys = ('title', 'season', 'episode', 'episode_title', 'container')
    if all(key in guess for key in required_keys):
        tv_show_path = os.path.join(tv_dir, guess['title'])

        if not os.path.exists(tv_show_path):
            os.mkdir(tv_show_path)

        season = 'Season {0}'.format(guess['season'])
        season_path = os.path.join(tv_show_path, season)

        if not os.path.exists(season_path):
            os.mkdir(season_path)

        destination_path = os.path.join(
            season_path,
            '{title} - S{season}E{episode} - {episode_title}.{container}'
                .format(
                    title=guess['title'],
                    season=str(guess['season']).zfill(2),
                    episode=str(guess['episode']).zfill(2),
                    episode_title=guess['episode_title'],
                    container=guess['container']
                )
        )

        if move:
            shutil.move(path, destination_path)
        else:
            shutil.copyfile(path, destination_path)
    else:
        action = 'move' if move else 'copy'

        command = [
            filebot_bin,
            '--action',
            action,
            '--db',
            'TheTVDB',
            '--format',
            '{n}/Season {s}/{n} - {s00e00} - {t}',
            '-non-strict',
            '-unixfs',
            '-rename',
            path,
            '--output',
            tv_dir
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE)

        if result.returncode != 0:
            pb_notify('Failed to rename {0} using filebot'.format(path))
        elif b'Skipped' in result.stdout and b'already exists' in result.stdout:
            pb_notify('Filebot skipped {0}: already exists'.format(path))


def handle_couchpotato(torrent):
    for index, file in torrent.files().items():
        file_path = os.path.join(torrent.downloadDir, file['name'])
        if file_path.endswith('rar'):
            paths = extract(file_path, download_dir)

            if paths:
                for path in paths:
                    guess = guessit.guessit(path)
                    move_movie(path, guess)


def handle_sonarr(torrent):
    for index, file in torrent.files().items():
        file_path = os.path.join(torrent.downloadDir, file['name'])
        if file_path.endswith('rar'):
            with tempfile.TemporaryDirectory() as temp_dir:
                paths = extract(file_path, temp_dir)

                if paths:
                    # Move extracted files to sonarr drone factory
                    for path in paths:
                        shutil.chown(path, group='plex')
                        os.chmod(path, 0o664)
                        shutil.move(path, drone_factory)


def handle_manual(torrent):
    auto_processed = False

    def handle_media(path, move):
        nonlocal auto_processed

        guess = guessit.guessit(path)

        if guess['type'] == 'episode':
            move_episode(path, guess, move)
            auto_processed = True
        elif guess['type'] == 'movie':
            move_movie(path, guess, move)
            auto_processed = True

    part_regex = re.compile('.*part(\d+).rar', re.IGNORECASE)
    for index, file in torrent.files().items():
        file_path = os.path.join(torrent.downloadDir, file['name'])
        if check_extension(file_path) and 'sample' not in file_path.lower():
            # Log and ignore mkv files of less than ~92MiB
            try:
                if os.path.getsize(file_path) >= 96811278:
                    handle_media(file_path, False)
                else:
                    syslog.syslog(
                        syslog.LOG_ERR, 'Detected false media file, skipping'
                    )
            except FileNotFoundError:
                syslog.syslog(syslog.LOG_ERR, 'Torrent file missing, skipping')
        elif file_path.endswith('rar'):
            # Ignore parts beyond the first in a rar series
            match = part_regex.match(file_path)
            if match and int(match.group(1)) > 1:
                continue

            with tempfile.TemporaryDirectory() as temp_dir:
                paths = extract(file_path, temp_dir)

                if paths:
                    for path in paths:
                        shutil.chown(path, group='plex')
                        os.chmod(path, 0o664)

                        handle_media(path, True)

    if auto_processed:
        pb_notify(
            textwrap.dedent(
                '''
                    Manually added torrent {0} finished downloading
                    and was auto-processed
                '''.format(torrent.name)
            ).strip()
        )
    else:
        pb_notify(
            'Manually added torrent {0} finished downloading'.format(
                torrent.name
            )
        )


def handle_finished_download():
    torrent_id = os.environ['TR_TORRENT_ID']
    syslog.syslog('Beginning processing of torrent {0}'.format(torrent_id))

    transmission_client = transmissionrpc.Client(
        transmission_host, port=transmission_port, user=transmission_user,
        password=transmission_password
    )
    torrent = transmission_client.get_torrent(torrent_id)

    # Make sure transmission called us with a completed torrent
    if torrent.progress != 100.0:
        syslog.syslog(syslog.LOG_ERR, 'Called with an incomplete torrent')
        sys.exit(1)

    if couchpotato_category in torrent.downloadDir:
        if not ignore_couchpotato:
            handle_couchpotato(torrent)
    elif sonarr_category in torrent.downloadDir:
        if not ignore_sonarr:
            handle_sonarr(torrent)
    else:
        handle_manual(torrent)

    # Immediately remove torrents that are not whitelisted (by tracker)
    if not whitelisted(torrent):
        transmission_client.remove_torrent(torrent_id)
        pb_notify('Removed non-whitelisted torrent {0}'.format(torrent.name))
