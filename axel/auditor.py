import os
import re
import subprocess

import guessit
import tmdbsimple as tmdb

from axel import config


def search_tmdb(query):
    search = tmdb.Search()
    response = search.movie(query=query)

    selection = None
    if search.results:
        for index, result in enumerate(search.results):
            print(
                str(index).zfill(2) + ') ',
                result['title'],
                result['id'],
                result['release_date'],
                result['popularity']
            )

        while True:
            try:
                choice = int(input('> '))
                # Need to compare to None explicitly since choice can be 0
                if choice is not None:
                    selection = search.results[choice]
                else:
                    print('Skipping...')
            except IndexError:
                print('Invalid selection')
            except ValueError:
                print('Not a number')
            else:
                break
    else:
        print('==> No matches found (searched for "{0}")'.format(query))

    return selection


def determine_quality(path):
    command = [
        config['mediainfo_bin'],
        '--Output=Video;%Width%',
        path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE)

    try:
        width = int(result.stdout.decode('utf-8'))
        if width >= 1900:
            return '1080p'
        elif width >= 1200:
            return '720p'
        elif width >= 440:
            return '480p'
        else:
            return None
    except ValueError:
            return None


def audit(mode):
    if mode == 'movies':
        audit_movies()
    elif mode == 'tv':
        audit_tv()
    elif mode == 'all':
        audit_movies()
        audit_tv()
    else:
        raise ValueError('unknown audit mode')


movie_format = re.compile(
    '(?P<name>(?P<title>.+) \(\d{4}\) ?- (?P<quality>\d{3,4})p)\.(?P<ext>.+)'
)
movie_dir_format = re.compile('.+ \(\d{4}\)', re.IGNORECASE)
def audit_movies():
    if config['tmdb_api_key']:
        tmdb.API_KEY = config['tmdb_api_key']
        for movie in os.listdir(config['movie_dir']):
            source_path = os.path.join(config['movie_dir'], movie)

            # Check the conformance of the movie dir naming itself
            if not movie_dir_format.match(movie):
                print('==> "{0}" does not match, searching...'.format(movie))

                selection = search_tmdb(movie)

                if selection:
                    new_name = '{name} ({year})'.format(
                        name=selection['title'],
                        year=str(selection['release_date'][:4])
                    )
                    dest_path = os.path.join(config['movie_dir'], new_name)

                    print('Changing from "{old}" to "{new}"'.format(
                        old=movie, new=new_name
                    ))

                    os.rename(source_path, dest_path)
                    # Set the source path to the renamed directory
                    source_path = dest_path

            movie_dir = source_path
            # Now we inspect the contents of each movie dir
            for entry in os.listdir(movie_dir):
                source_path = os.path.join(movie_dir, entry)
                # Don't try to process subtitles, etc
                if not entry.endswith('mkv'):
                    continue

                match = movie_format.match(entry)
                if match:
                    if match.group('quality') != '1080':
                        print(
                            '==> WARNING: non-1080p detected: {0}'.format(
                                entry
                            )
                        )
                else:
                    print('==> {0} does not match, searching...'.format(entry))

                    guess = guessit.guessit(entry)
                    selection = search_tmdb(guess['title'])

                    if selection:
                        quality = determine_quality(source_path)
                        if quality:
                            name_format = '{name} ({year}) - {quality}.{ext}'
                            new_name = name_format.format(
                                name=selection['title'],
                                year=str(selection['release_date'][:4]),
                                quality=quality,
                                ext=guess['container']
                            )
                            dest_path = os.path.join(movie_dir, new_name)

                            print('Changing from "{old}" to "{new}"'.format(
                                old=entry, new=new_name
                            ))

                            os.rename(source_path, dest_path)
                        else:
                            print('==> Failed to determine quality')

        print('Finished!')
    else:
        print('Register for an API key from The Movie DB first.')


def audit_tv():
    pass
