import datetime
import pushbullet
import textwrap
import transmissionrpc

from axel import config


def clean():
    transmission_client = transmissionrpc.Client(
        config['transmission']['host'], port=config['transmission']['port']
    )

    pushbullet_client = pushbullet.Pushbullet(config['pushbullet_key'])

    torrents = transmission_client.get_torrents()
    now = datetime.datetime.now()

    time_threshold = config['transmission']['time_threshold']
    for torrent in torrents:
        if torrent.status == 'seeding':
            done = torrent.date_done
            diff = now - done

            if diff.days >= time_threshold:
                # TODO: Use pb_notify instead
                pushbullet_client.push_note(
                    'Axel',
                    textwrap.dedent(
                        '''
                            Torrent {torrent} older than {days} days:
                            removing (with data)
                        '''.format(torrent=torrent.name, days=time_threshold)
                    ).strip()
                )

                transmission_client.remove_torrent(
                    torrent.id, delete_data=True
                )
            elif torrent.ratio >= config['transmission']['ratio_threshold']:
                # TODO: Use pb_notify instead
                pushbullet_client.push_note(
                    'Axel',
                    textwrap.dedent(
                        '''
                            Torrent {0} reached threshold ratio or higher:
                            removing (with data)
                        '''.format(torrent.name)
                    ).strip()
                )

                transmission_client.remove_torrent(
                    torrent.id, delete_data=True
                )
