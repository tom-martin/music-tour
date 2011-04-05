import sys
from last_fm import LastFmService

import logging

if len(sys.argv) < 3:
    print "Usage find.py <artist name> <other artist name>"
    exit()

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('music_tour')

last_fm = LastFmService()

artist_one = sys.argv[1]
artist_two = sys.argv[2]

logger.debug("Searching for " + artist_one + " to " + artist_two)

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
    print route
    if len(last_fm.loading_failures) > 0:
        logger.debug(last_fm.loading_failures)
    
    print "Cache hit percentage " + str(last_fm.get_cache_percentage())
else:
    print "Fail"
