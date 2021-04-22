# Copyright (C) 2021 Frederick W. Nielsen
#
# This file is part of flowroute-things.
#
# flowroute-things is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# flowroute-things is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with flowroute-things.  If not, see <http://www.gnu.org/licenses/>.

"""
Purchases a block of available DIDs from flowroute via API
"""

import os
from time import sleep

import requests
import yaml

# specifies separate config file containing non-portable parameters
# looks for a YAML file in the user's home directory under the subfolder "Personal-Local"
# i.e. c:\users\jsmith\Personal-Local\config.yml
CONFIG_FILE = os.path.join(os.path.expanduser('~'), "Personal-Local", "config.yml")

STATUS_PURCHASE_WAIT = 'Purchasing number: '
STATUS_PURCHASE_SUCCESS = ' success!'

ERROR_INVALID = 'Invalid NANP E164 number spec, please examine STARTS_WITH and ENDS_WITH settings'
ERROR_LARGE = 'Block size exceeds MAX_PURCHASE size of '

FR_NAPI_URL = 'https://api.flowroute.com/v2/numbers/'

STARTS_WITH = 14085551200
ENDS_WITH = 14085551214

# sets the maximum block size that can be purchased in one execution to avoid large purchase errors
MAX_PURCHASE = 15
# sets whether you want CNAM dipping enabled on the numbers ($ per call)
CNAM_LOOKUPS_ENABLED = True
# sets whether you want SMS\MMS messaging enabled on the numbers ($ per inbound\outbound message)
MESSAGING_ENABLED = False

def main():
    """purchase those numbers!"""

    # grab non-portable parameters from external config file
    with open(CONFIG_FILE, 'r') as config_file:
        config_params = yaml.full_load(config_file)

    # you'll need your own flowroute API creds
    fr_config = config_params['flowroute']
    fr_auth = (fr_config['access_key'], fr_config['secret_key'])

    fr_api_session = requests.Session()

    # check is valid NANP range
    if STARTS_WITH < 12012000000 or STARTS_WITH > 19989999999 or \
        ENDS_WITH < 12012000000 or ENDS_WITH > 19989999999:
        print(ERROR_INVALID)
        raise SystemExit

    # check if block too big
    if (ENDS_WITH - STARTS_WITH +1) > MAX_PURCHASE:
        print(f'{ERROR_LARGE}{MAX_PURCHASE}')
        raise SystemExit


    current = STARTS_WITH
    while current <= ENDS_WITH:
        print(f'{STATUS_PURCHASE_WAIT}{current}... ', end='')
        post = fr_api_session.post(f'{FR_NAPI_URL}{current}',
                                   auth=fr_auth,
                                   params = {'cnam_lookups_enabled': CNAM_LOOKUPS_ENABLED,
                                             'messaging_enabled': MESSAGING_ENABLED}
                                   )

        if post.status_code == 201:
            print('purchased')
        elif post.status_code == 429:
            print ('retrying...')
            sleep(.5)
            continue
        else:
            print('ISSUE:')
            print(f'{post.status_code}: {post.json()["errors"][0]["detail"]}', end='\n\n')

        current += 1


if __name__ == "__main__":
    main()
