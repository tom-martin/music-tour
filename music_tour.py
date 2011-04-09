import sys
from last_fm import LastFmService
from spotify import SpotifyMetaService
import random

import logging

def find_path(artist_one, artist_two, blacklist):
    print blacklist

    artist_one_out = set()
    artist_one_out.add(artist_one)
    artist_one_parent = {artist_one: None}

    artist_two_out = set()
    artist_two_out.add(artist_two)
    artist_two_parent = {artist_two: None}

    step_count = 0

    linking_artist = None

    queue_one = [artist_one]
    queue_two = [artist_two]
    while len(queue_one) > 0 and len(queue_two) > 0 and linking_artist == None:
        step_count+=1
        parent = queue_one[0]
        queue_one.remove(parent)

        artists = last_fm.get_similar_for_artist(parent)
        for artist in artists:
            if not artist in artist_one_out:
                artist_one_out.add(artist)
                if not artist in blacklist:
                    queue_one.append(artist)
                    artist_one_parent[artist] = parent

                    if artist in artist_two_out:
                        linking_artist = artist
                        break;

        if linking_artist != None:
            break

        parent = queue_two[0]
        queue_two.remove(parent)

        artists = last_fm.get_similar_for_artist(parent)
        for artist in artists:
            if not artist in artist_two_out:
                artist_two_out.add(artist)
                if not artist in blacklist:
                    queue_two.append(artist)
                    artist_two_parent[artist] = parent

                    if artist in artist_one_out:
                        linking_artist = artist
                        break;

        if linking_artist != None:
            break


    if linking_artist != None:
        route = []
        current = linking_artist
        while current != None:
            route.insert(0, current)
            current = artist_one_parent[current]

        current = artist_two_parent[linking_artist]
        while current != None:
            route.append(current)
            current = artist_two_parent[current]

        print linking_artist + " is in both graphs (" + str(step_count) + ")"

    return route

if len(sys.argv) < 3:
    print "Usage find.py <artist name> <other artist name>"
    exit()

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('music_tour')

last_fm = LastFmService()
spotify = SpotifyMetaService()

artist_one = sys.argv[1]
artist_two = sys.argv[2]

if len(spotify.get_tracks(artist_one)) == 0:
    print "No spotify tracks found for " + artist_one
    exit()

if len(spotify.get_tracks(artist_two)) == 0:
    print "No spotify tracks found for " + artist_two
    exit()

blacklist = set()
if len(sys.argv) > 3:
    for blacklisted in sys.argv[3].split(','):
        blacklist.add(blacklisted)

logger.debug("Searching for " + artist_one + " to " + artist_two)

route = []
tracks = []
while len(tracks) == 0:
    route = find_path(artist_one, artist_two, blacklist)
    print "Cache hit percentage " + str(last_fm.get_cache_percentage())
    if len(last_fm.loading_failures) > 0:
        logger.warning(last_fm.loading_failures)


    if len(route) == 0:
        print "Fail"
        break

    for artist in route:
        artist_tracks = spotify.get_tracks(artist)
        if len(artist_tracks) > 0:
            tracks.append(random.choice(artist_tracks))
        else:
            # start again
            print "Blacklisting " + artist + " (no spotify tracks found) and starting over"
            tracks = []
            blacklist.add(artist)
            break

if len(tracks) > 0:
    print route
    print
    print "Playlist:"
    for track in tracks:
        print track    
