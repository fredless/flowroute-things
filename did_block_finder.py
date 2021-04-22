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
Prompts for an E164 prefix and a minimum block size, then queries flowroute for available
contiguous number blocks.
"""

import itertools
import os
import shutil
from itertools import groupby
from operator import itemgetter

import requests
import yaml

# specifies separate config file containing non-portable parameters
# looks for a YAML file in the user's home directory under the subfolder "Personal-Local"
# i.e. c:\users\jsmith\Personal-Local\config.yml
CONFIG_FILE = os.path.join(os.path.expanduser('~'), "Personal-Local", "config.yml")

STATUS_QUERY_WAIT = 'Querying flowroute for available numbers, this may take a while... '

FR_NAPI_URL = 'https://api.flowroute.com/v2/numbers/available'
FR_NAPI_PAGE = 200

STARTS_WITH = 1408
MIN_SIZE = 15

# we can also look for interesting digit strings while we hunt for blocks
UNIQUE_DIGITS = ['37587', '9922']

SPINNER = itertools.cycle(['-', '/', '|', '\\'])
FIN = ' finished.'

def print_status(text, linefeed=0):
    """output refreshable status line"""
    text = f'{next(SPINNER)} {text}'
    screen_width = shutil.get_terminal_size((80, 0))[0]
    print(text +
          ' ' * (screen_width-(len(text)+1)) +
          '\b' * (screen_width -1) +
          '\n' * linefeed,
          end='')

def main():
    """look for numbers"""

    # grab non-portable parameters from external config file
    with open(CONFIG_FILE, 'r') as config_file:
        config_params = yaml.full_load(config_file)

    # you'll need your own flowroute API creds
    fr_config = config_params['flowroute']
    fr_auth = (fr_config['access_key'], fr_config['secret_key'])

    fr_api_session = requests.Session()

    # store list of returned numbers as strings
    str_num_list = []
    offset = 0

    # query numbers one page at a time
    more_results = True
    while more_results:
        print_status(f'{STATUS_QUERY_WAIT}{offset}')
        response = fr_api_session.get (FR_NAPI_URL,
                                       auth=fr_auth,
                                       params={'order_by': 'tn,asc',
                                               'limit': FR_NAPI_PAGE,
                                               'offset': offset,
                                               'starts_with': 1408})
        if response.status_code == 200:
            result = response.json()

            # drop each returned phone number into list
            for record in result['data']:
                str_num_list.append(record['id'])

            if 'next' in result['links']:
                # another page of results awaits
                offset += FR_NAPI_PAGE
            else:
                # we're at the last page
                print_status(f'{STATUS_QUERY_WAIT}{FIN}', linefeed=2)
                more_results = False

        else:
            # anything other than 200 comes back, error out
            print(f'ERROR {response.status_code}:{response.json()}')


    # convert list of number strings to integers for searching
    int_num_list = [int(i) for i in str_num_list]

    # output list of ranges that meet criteria
    for _,g in groupby(enumerate(int_num_list),lambda x:x[0]-x[1]):
        group = map(itemgetter(1), g)
        group = list(map(int,group))
        if group[0] + MIN_SIZE - 1 <= group[-1]:
            how_many = group[-1] - group[0] + 1
            print(f'Block of {how_many}: {group[0]} - {group[-1]}')

    print()

    # bonus: looks for interesting strings in numbers queried
    for number in str_num_list:
        if any(match in number for match in UNIQUE_DIGITS):
            print(f'Interesting string in {number}')

    print()

if __name__ == "__main__":
    main()
