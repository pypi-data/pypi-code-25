# Scrapy settings for versiontracker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

from xdg.BaseDirectory import save_cache_path

from ._version import __version__ as version


BOT_NAME = 'versiontracker'

SPIDER_MODULES = ['versiontracker.spiders']
NEWSPIDER_MODULE = 'versiontracker.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'versiontracker/{} (+http://version-tracker.rtfd.io)'.format(
    version)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 64

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS/2
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
   'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
   'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
   'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
   'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.corestats.CoreStats': None,
   'scrapy.extensions.logstats.LogStats': None,
   'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'versiontracker.pipelines.Pipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 0
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = CONCURRENT_REQUESTS_PER_DOMAIN/2
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = save_cache_path('versiontracker')
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'

# Additional settings
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
LOG_ENABLED = True
LOG_LEVEL = 'WARNING'
STATS_CLASS = 'scrapy.statscollectors.DummyStatsCollector'
STATS_DUMP = False
