'''Application environment configuration.

Configuration keys that can be overridden through environment variables:

  * CHRONOLOGER_USERNAME
  * CHRONOLOGER_PASSWORD
  * CHRONOLOGER_STORAGE_DSN
  * CHRONOLOGER_HOST
  * CHRONOLOGER_PORT
  * CHRONOLOGER_THREAD_POOL

'''


import os


__all__ = 'production', 'development', 'test_suite'


base = {
  'global' : {
    # HTTP server
    'server.socket_host' : os.environ.get('CHRONOLOGER_HOST', '127.0.0.1'),
    'server.socket_port' : int(os.environ.get('CHRONOLOGER_PORT', 8080)),
    'server.thread_pool' : int(os.environ.get('CHRONOLOGER_THREAD_POOL', 8)),
    # file change reload
    'engine.autoreload.on' : False,
    # URL trailing slash
    'tools.trailing_slash.on' : False,
    # logging
    'log.screen'      : False,
    'log.access_file' : None,
    'log.error_file'  : None,
  },
  'logging' : {
    'disable_existing_loggers' : False,
    'version'                  : 1,
    'formatters'               : {
      'print' : {
        'format' : '%(levelname)-8s %(name)-15s %(message)s'
      },
    },
    'handlers' : {
      'console' : {
        'class'     : 'logging.StreamHandler',
        'formatter' : 'print'
      },
    },
    'root' : {
      'handlers' : ['console'],
    }
  },
  'storage' : {
    'dsn' : os.environ.get('CHRONOLOGER_STORAGE_DSN'),
  },
  'auth' : {
    'username' : os.environ.get('CHRONOLOGER_USERNAME', 'logger'),
    'password' : os.environ.get('CHRONOLOGER_PASSWORD', ''),
  },
  'app' : {
    'api' : {
      '/' : {
        'request.dispatch' : {
          '()' : 'cherrypy._cpdispatch.MethodDispatcher'
        }
      }
    },
    'static' : {
      '/' : {
        'tools.staticdir.on'    : True,
        'tools.staticdir.dir'   : os.path.join(os.path.dirname(__file__), 'static'),
        'tools.staticdir.index' : 'index.html'
      }
    }
  },
}

production = (base, {
  'global' : {
    'server.socket_host' : os.environ.get('CHRONOLOGER_HOST', '0.0.0.0'),
    # compression
    'tools.gzip.on'         : True,
    'tools.gzip.mime_types' : ['application/json', 'application/javascript'],
    # authentication
    'tools.auth_basic.on'            : True,
    'tools.auth_basic.realm'         : 'Chronologer',
    'tools.auth_basic.checkpassword' : 'ext://chronologer.authenticate'
  },
  'logging' : {
    'handlers' : {
      'console' : {
        'level' : 'INFO',
      },
    },
    'root' : {
      'level' : 'INFO',
    },
  },
})

development = (base, {
  'storage' : {
    'dsn' : os.environ.get('CHRONOLOGER_STORAGE_DSN', 'mysql://guest@localhost/chronologer'),
  },
  'logging' : {
    'handlers' : {
      'console' : {
        'level' : 'DEBUG',
      },
    },
    'root' : {
      'level' : 'DEBUG',
    },
  },
  'app' : {
    'api' : {
      '/' : {
        'tools.response_headers.on'      : True,
        'tools.response_headers.headers' : [
          ('Access-Control-Allow-Origin', '*'),
          ('Access-Control-Expose-Headers', 'X-Record-Count, X-Record-Group')
        ]
      }
    }
  }
})

test_suite = (base, {
  'global' : {
    # Remove these, as they prevent CherryPy simulator from working
    'server.socket_host' : None,
    'server.socket_port' : None,
  },
  'storage' : {
    'dsn' : os.environ.get('CHRONOLOGER_STORAGE_DSN', 'mysql://guest@127.0.0.1/chronologer_test'),
  },
  'logging' : {
    'handlers' : {
      'console' : {
        'level' : 'WARNING',
      },
    },
    'root' : {
      'level' : 'WARNING',
    },
  }
})

