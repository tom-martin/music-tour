import urllib2
import urllib
from time import time, sleep
import logging
import os

logger = logging.getLogger('last_fm')

class LastFmService:
    def __init__(self):
        self.last_request_time = time()
        self.loading_failures = []
        self.cache_count = 0
        self.last_count = 0

        self.CACHE_PATH = './last_cache'

        try:
            os.makedirs(self.CACHE_PATH)
        except OSError, e:
            if not os.path.exists(self.CACHE_PATH):
                raise e


    def get_from_cache(self, artist_name):
        try:
            sim_file = open(self.CACHE_PATH + '/' + artist_name + '.txt')
            similar_feed = sim_file.read()
            logger.debug("Found from cache")
            return similar_feed
        except IOError, e:
            return None

    def write_to_cache(self, artist_name, feed):
        sim_file = open(self.CACHE_PATH + '/' + artist_name + '.txt', 'w')
        sim_file.write(feed)

    def escape_artist_name(self, artist_name):
        # quote_plus THEN quote, seems to be the only thing that works, also manually replace
        # . with %2E before the last quote
        return urllib.quote(urllib.quote_plus(artist_name).replace('.', '%2E'))

    def get_similar_for_artist(self, artist_name):

        artist_name_esc = self.escape_artist_name(artist_name)

        logger.debug("Searching for " + artist_name)

        similar_feed = self.get_from_cache(artist_name_esc)

        if similar_feed == None:
            time_diff = time() - self.last_request_time
            while time_diff < 1:
                logger.info("Waiting for " + str(1 - time_diff))
                sleep(1 - time_diff)
                time_diff = time() - self.last_request_time

            url = 'http://ws.audioscrobbler.com/2.0/artist/' + artist_name_esc + '/similar.txt'
            try:
                result = urllib2.urlopen(url)
            except Exception, e:
                logger.warning("Failed to load " + artist_name + ": " + str(e))
                loading_failures.append(artist_name + ": " + str(e))
                return []

            similar_feed = result.read()
            self.last_request_time = time()

            self.write_to_cache(artist_name_esc, similar_feed)
            self.last_count += 1
            logger.debug("Got from last.fm")
        else:
            self.cache_count += 1
    
    
        similar = []
        lines = similar_feed.splitlines()
        for line in lines:
            line_split = line.split(',')
            similarity = float(line_split[0])
            if similarity < 0.2:
                break

            artist = line_split[2]
            artist = artist.replace('&amp;', '&')
            artist = artist.replace('&quot;', '\'')
            similar.append(artist)

        
    
        return similar

    def get_cache_percentage(self):
        return (float(self.cache_count) / (self.cache_count + self.last_count)) * 100

