#!/usr/bin/env python3

import json
import toml
import requests
import datetime

config = toml.load('config.toml')
api_key = config['pinboard']['api_key']

pinboard_endpoint = 'https://api.pinboard.in/v1/{}?auth_token=' + api_key

default_params = {'format': 'json'}

def req_params(in_params):
    return dict(list(in_params.items()) + list(default_params.items()))

def get(method, params):
    return requests.get(
            pinboard_endpoint.format(method),
            params=req_params(params))

def load_pocket_items(pocket_json):
    with open(pocket_json, 'r') as fp:
        return json.load(fp)

def pocket_item_to_pinboard_params(pocket_item, replace=False):
    params = dict()
    params['url'] = pocket_item['given_url']
    params['extended'] = ''

    if pocket_item['resolved_title']:
        params['description'] = pocket_item['resolved_title']
    elif pocket_item['given_title']:
        params['description'] = pocket_item['given_title']
    else:
        params['description'] = params['url']
        params['extended'] += 'pocket_bad_title\n'

    if 'tags' in pocket_item:
        params['tags'] = ','.join([t.replace(' ', '-') for t in pocket_item['tags']])

    params['dt'] = datetime.datetime.utcfromtimestamp(
            int(pocket_item['time_added'])).isoformat()+'Z'

    if replace:
        params['replace'] = 'yes'
    else:
        params['replace'] = 'no'

    if pocket_item['status'] == '0':
        params['toread'] = 'yes'
    elif pocket_item['status'] == '1':
        params['toread'] = 'no'

    # Starred isn't supported by the Pinboard API :(
    if pocket_item['favorite'] == '0':
        #params['starred'] = 'no'
        pass
    elif pocket_item['favorite'] == '1':
        #params['starred'] = 'yes'
        params['extended'] += 'pocket_favorite\n'

    return params


if __name__ == "__main__":
    pocket_items = load_pocket_items('all.json')
    for idx,item in enumerate(pocket_items):
        params = pocket_item_to_pinboard_params(item)
        resp = get('posts/add', params)
        if resp.status_code != 200:
            print("### {} : Unexpected HTTP response code {}".format(idx, resp.status_code))
            print("    Response: {}".format(resp.json()))
        elif resp.json()['result_code'] != 'done':
            print("### {} : Unexpected result code '{}'".format(idx, resp.json()['result_code']))
            print("    Response: {}".format(resp.json()))
        else:
            print("{} success".format(idx))

