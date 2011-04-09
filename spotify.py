import urllib2
import urllib
from time import time, sleep
import logging
import os
import xml.etree.ElementTree as etree

logger = logging.getLogger('spotify')

class SpotifyMetaService:
    def __init__(self):
        self.last_request_time = time()
        self.CACHE_PATH = './spotify_cache'
        self.REQUIRED_TERRITORY = "GB"
        self.MAX_TRACKS = 5
        

        try:
            os.makedirs(self.CACHE_PATH)
        except OSError, e:
            if not os.path.exists(self.CACHE_PATH):
                raise e


    def get_from_cache(self, cache_key):
        try:
            sim_file = open(self.CACHE_PATH + '/' + cache_key + '.txt')
            similar_feed = sim_file.read()
            logger.debug("Found from cache " + cache_key)
            return similar_feed
        except IOError, e:
            return None

    def write_to_cache(self, cache_key, cache_value):
        sim_file = open(self.CACHE_PATH + '/' + cache_key + '.txt', 'w')
        sim_file.write(cache_value)
    
    def get_tracks(self, artist_name, ):

        artist_name_esc = urllib.quote(artist_name)
        tracks_string = self.get_from_cache(artist_name_esc)

        if tracks_string == None:

            time_diff = time() - self.last_request_time
            while time_diff < 1:
                logger.info("Waiting for " + str(1 - time_diff))
                sleep(1 - time_diff)
                time_diff = time() - self.last_request_time

            url = 'http://ws.spotify.com/search/1/track?q=' + artist_name_esc
            try:
                print "Loading " + url
                result = urllib2.urlopen(url)
                tracks_string = result.read()
                self.last_request_time = time()
                self.write_to_cache(artist_name_esc, tracks_string)

            except Exception, e:
                logger.warning("Failed to load " + artist_name + ": " + str(e))
                # TODO
                #self.loading_failures.append(artist_name + ": " + str(e))
                return []

        tracks = etree.fromstring(tracks_string)
        # Fucking namespaces!
        tracks = filter(lambda c: c.tag == '{http://www.spotify.com/ns/music/1}track', tracks)

        matching_tracks = []
        for track in tracks:
            track_artist_name = self.get_artist_name(track)
            if track_artist_name != None and track_artist_name.lower() == artist_name.lower() and self.track_available_in_req_territories(track):
                matching_tracks.append(track.attrib['href'])
        
            if len(matching_tracks) >= self.MAX_TRACKS:
                break

        return matching_tracks

    def track_available_in_req_territories(self, track):
        album = track.find('{http://www.spotify.com/ns/music/1}album') 
        availability = None
        if album != None:
            availability = album.find('{http://www.spotify.com/ns/music/1}availability')
        territories = None
        if availability != None:
            territories = availability.find('{http://www.spotify.com/ns/music/1}territories')

        if territories != None:
            return territories.text != None and "GB" in territories.text

    def get_artist_name(self, track):
        track_artist = track.find('{http://www.spotify.com/ns/music/1}artist')
        if track_artist:
            return track_artist.find('{http://www.spotify.com/ns/music/1}name').text.encode('utf-8')

