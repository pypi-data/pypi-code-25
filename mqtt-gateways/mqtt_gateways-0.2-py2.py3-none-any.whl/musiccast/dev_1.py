'''
Created on 8 May 2018

@author: PierPaolo
'''

FEATURES = {
  'response_code': 0,
  'system': {
    'func_list': [
      'wired_lan',
      'wireless_lan',
      'wireless_direct',
      'network_standby',
      'auto_power_standby',
      'bluetooth_tx_setting',
      'airplay',
      'network_reboot'
    ],
    'zone_num': 1,
    'input_list': [
      {
        'id': 'napster',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': True,
        'play_info_type': 'netusb'
      },
      {
        'id': 'spotify',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'juke',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': True,
        'play_info_type': 'netusb'
      },
      {
        'id': 'qobuz',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': True,
        'play_info_type': 'netusb'
      },
      {
        'id': 'tidal',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': True,
        'play_info_type': 'netusb'
      },
      {
        'id': 'deezer',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': True,
        'play_info_type': 'netusb'
      },
      {
        'id': 'airplay',
        'distribution_enable': False,
        'rename_enable': False,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'mc_link',
        'distribution_enable': False,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'server',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'net_radio',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'bluetooth',
        'distribution_enable': True,
        'rename_enable': False,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'usb',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'netusb'
      },
      {
        'id': 'tuner',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'tuner'
      },
      {
        'id': 'cd',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'cd'
      },
      {
        'id': 'digital',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'none'
      },
      {
        'id': 'aux',
        'distribution_enable': True,
        'rename_enable': True,
        'account_enable': False,
        'play_info_type': 'none'
      }
    ],
    'ymap_list': [
      'vtuner'
    ]
  },
  'zone': [
    {
      'id': 'main',
      'func_list': [
        'power',
        'sleep',
        'volume',
        'mute',
        'signal_info',
        'prepare_input_change',
        'link_control'
      ],
      'input_list': [
        'napster',
        'spotify',
        'juke',
        'qobuz',
        'tidal',
        'deezer',
        'airplay',
        'mc_link',
        'server',
        'net_radio',
        'bluetooth',
        'usb',
        'tuner',
        'cd',
        'digital',
        'aux'
      ],
      'link_control_list': [
        'speed',
        'standard',
        'stability'
      ],
      'range_step': [
        {
          'id': 'volume',
          'min': 0,
          'max': 63,
          'step': 1
        }
      ]
    }
  ],
  'tuner': {
    'func_list': [
      'fm',
      'rds',
      'dab'
    ],
    'range_step': [
      {
        'id': 'fm',
        'min': 87500,
        'max': 108000,
        'step': 50
      }
    ],
    'preset': {
      'type': 'separate',
      'num': 30
    }
  },
  'netusb': {
    'func_list': [
      'recent_info',
      'play_queue',
      'mc_playlist'
    ],
    'preset': {
      'num': 40
    },
    'recent_info': {
      'num': 40
    },
    'play_queue': {
      'size': 200
    },
    'mc_playlist': {
      'size': 200,
      'num': 5
    },
    'net_radio_type': 'vtuner',
    'vtuner_fver': 'A',
    'pandora': {
      'sort_option_list': [
        'date',
        'alphabet'
      ]
    }
  },
  'distribution': {
    'server_zone_list': [
      'main'
    ]
  },
  'ccs': {
    'supported': True
  }
}

def get_feature(flist):
    ''' Returns the branch from the getFeatures tree.'''
    branch = FEATURES
    if isinstance(flist, basestring): # Python 3: isinstance(arg, str)
        flist = (flist,)
    for arg in flist:
        if isinstance(arg, basestring):
            try: branch = branch[arg]
            except KeyError:
                return ''.join(('Argument <', str(arg), '> not found in current branch: ', str(branch)))
            except TypeError:
                return ''.join(('The current branch is not a dictionary: ', str(branch)))
        else: # assume arg is a pair (key, value)
            try:
                key = arg[0]
                value = arg[1]
            except (IndexError, TypeError):
                return ''.join(('Argument <', str(arg), '> should be a pair.'))
            found = False
            for obj in branch: # assume branch is an array
                try: found = (obj[key] == value)
                except KeyError:
                    return ''.join(('Key <', str(key), '> not found in current branch: ', str(branch)))
                except TypeError:
                    return ''.join(('The current branch is not a dictionary: ', str(branch)))
                if found: break
            if not found:
                return ''.join(('Value <', str(value), '> for key <', str(key),
                                '> not found in array.'))
            branch = obj
    return branch

if __name__ == '__main__':
    print get_feature(('tuner', 'preset', 'num'))
    print get_feature('response_code')
    print get_feature(('zone', ('id', 'main'), 'range_step', ('id', 'volume'), 'max'))

