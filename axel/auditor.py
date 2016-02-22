import os
import re

import tmdbsimple as tmdb

from axel import config


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


movie_dir_format = re.compile('.+ \(\d{4}\)', re.IGNORECASE)
def audit_movies():
    if config['tmdb_api_key']:
        tmdb.API_KEY = config['tmdb_api_key']
        search = tmdb.Search()
        for movie in os.listdir(config['movie_dir']):
            if not movie_dir_format.match(movie):
                print('==> {0} does not match, searching...'.format(movie))
                response = search.movie(query=movie)

                if search.results:
                    for index, result in enumerate(search.results):
                        print(
                            str(index).zfill(2) + ') ',
                            result['title'],
                            result['id'],
                            result['release_date'],
                            result['popularity']
                        )

                    selection = None
                    while True:
                        choice = input('> ')
                        try:
                            if choice:
                                selection = search.results[int(choice)]
                        except IndexError:
                            print('Invalid selection')
                        except ValueError:
                            print('Not a number')
                        else:
                            break

                    if choice:
                        source_path = os.path.join(config['movie_dir'], movie)
                        new_name = '{name} ({year})'.format(
                            name=selection['title'],
                            year=str(selection['release_date'][:4])
                        )
                        dest_path = os.path.join(config['movie_dir'], new_name)

                        print('Changing from "{old}" to "{new}"'.format(
                            old=movie, new=new_name
                        ))

                        os.rename(source_path, dest_path)
                    else:
                        print('Skipping')
                else:
                    print('==> No matches found')
        print('Finished!')
    else:
        print('Register for an API key from The Movie DB first.')


def audit_tv():
    pass
