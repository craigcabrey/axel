# axel

Opinionated automation of media handling, placement, and organization.

## About

`axel` fills in the gaps of other media handling systems. For example, it has
the ability to automatically detect, test, and extract archived downloads to
the correct location (which is potentially an import location for another
system).

This system is intended to work with the following:

* libunrar
* filebot
* mediainfo
* Python 3.5+
* Sonarr
* CouchPotato
* Transmission
* Linux/BSD

Pushbullet is a available as an optional mechanism to notify of events that
occur during processing. If you wish to use a specific channel when notifying,
specify it in the configuration.

## Getting Started

First, install the dependencies required to run:
`python3 setup.py install`.

Next, copy the provided configuration file to `/etc/axel.conf` and update the
indicated values with appropriate information.

Finally, update your Transmission settings to execute `axel` as a post-download
script:

```js
{
  [...]
  "script-torrent-done-enabled": true,
  "script-torrent-done-filename": "/usr/bin/axelctl",
  [...]
}
```

## Naming Conventions

`axel` follows Plex naming conventions wherever possible. This is not
configurable.

Movies:

`{root}/{Title} ({Year})/{Title} - ({Year}) - {Quality}.{ext}`

TV Shows:

`{root}/{Title}/Season {Season No}/{Title} - S{Season No}E{Episode No} - {Episode Name}.{ext}`

There is an audit feature to assist you with migrating existing media to the
convention:

`axelctl --audit movies`

This is an interactive process that involves querying
[The Movie DB](https://www.themoviedb.org/), which means you need to obtain an
API key from them.

TV Show auditing support is coming soon.

## Troubleshooting

The most common issues relate to permissions and renaming.

### Permissions

To correct permission issues, ensure the caller (typically the `transmission`
user) has permissions to write to the directories indicated in the
configuration file. This can be accomplished by creating a `media` group, for
example:

```
drwxrwxr-x 189 plex media 189 Feb 16 20:52 movies
drwxrwxr-x 189 plex media 189 Feb 16 20:52 tv
drwxrwxr-x 189 transmission media 189 Feb 16 20:52 downloads
```

Where `plex` and `transmission` are both members of the `media` group.

### Renaming

In some instances, there is not enough information in the torrent metadata to
determine proper renaming.

For all other problems, open an issue with the specific error.
