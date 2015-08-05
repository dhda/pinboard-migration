#!/usr/bin/env python3

import json
import toml
from pocket import Pocket

def resp_to_sorted_list(list_dict):
    ordered_keys = sorted(list_dict, key=lambda k: list_dict[k]['sort_id'])
    return [list_dict[k] for k in ordered_keys]

def dump_to_json(obj, filename):
    with open(filename, 'w') as fp:
        json.dump(obj, fp, indent=4)

config = toml.load('config.toml')

pocket = Pocket(config['pocket']['consumer_key'], config['pocket']['access_token'])
archived_resp = pocket.get(state='archive', detailType='complete', sort='oldest')
unread_resp = pocket.get(state='unread', detailType='complete', sort='oldest')
all_resp = pocket.get(state='all', detailType='complete', sort='oldest')

archived_list = resp_to_sorted_list(archived_resp[0]['list'])
unread_list = resp_to_sorted_list(unread_resp[0]['list'])
all_list = resp_to_sorted_list(all_resp[0]['list'])

dump_to_json(archived_list, 'archived.json')
dump_to_json(unread_list, 'unread.json')
dump_to_json(all_list, 'all.json')
