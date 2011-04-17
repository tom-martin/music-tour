import sys
import music_tour
import logging

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) < 3:
    print "Usage find.py <artist name> <other artist name>"
    exit()

artist_one = sys.argv[1]
artist_two = sys.argv[2]

blacklist = set()
if len(sys.argv) > 3:
    for blacklisted in sys.argv[3].split(','):
        blacklist.add(blacklisted)

print "Searching for " + artist_one + " to " + artist_two

tracks = []
route = music_tour.find_spotify_path(artist_one, artist_two, blacklist)
tracks = music_tour.get_random_tracks_for_route(route)

if len(tracks) > 0:
    print route
    print
    print "Playlist:"
    for track in tracks:
        print track  
