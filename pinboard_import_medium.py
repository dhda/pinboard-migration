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

def load_medium_recs(med_rec_json):
    with open(med_rec_json, 'r') as fp:
        recs_json = json.load(fp)

    posts = recs_json['payload']['posts']
    user_map = recs_json['payload']['references']['User']
    collection_map = recs_json['payload']['references']['Collection']

    return (posts, user_map, collection_map)

def post_to_url(post, user_map, collection_map):
    if post['homeCollectionId']:
        user_part = collection_map[post['homeCollectionId']]['slug']
    else:
        user_part = "@{}".format(user_map[post['creatorId']]['username'])

    return "https://medium.com/{}/{}".format(user_part, post['uniqueSlug'])

def medium_rec_to_pinboard_params(rec, user_map, collection_map, replace=False):
    params = dict()
    params['url'] = post_to_url(rec, user_map, collection_map)
    params['extended'] = ''
    params['description'] = rec['title']

    params['tags'] = ','.join(
            ['medium-recommendation'] +
            ['medium-'+t['slug'] for t in rec['virtuals']['tags']])

    params['dt'] = datetime.datetime.utcfromtimestamp(
            int(int(rec['virtuals']['userPostRelation']['votedAt'])/1000)).isoformat()+'Z'

    if replace:
        params['replace'] = 'yes'
    else:
        params['replace'] = 'no'

    params['toread'] = 'no'
    params['extended'] = "{} {}".format(rec['virtuals']['subtitle'], rec['virtuals']['emailSnippet'])

    return params


if __name__ == "__main__":
    medium_recs = load_medium_recs('med_recs_full.json')
    for idx,rec in enumerate(medium_recs[0]):
        params = medium_rec_to_pinboard_params(rec, medium_recs[1], medium_recs[2])
        resp = get('posts/add', params)
        if resp.status_code != 200:
            print("### {} : Unexpected HTTP response code {}".format(idx, resp.status_code))
            print("    Response: {}".format(resp.json()))
        elif resp.json()['result_code'] != 'done':
            print("### {} : Unexpected result code '{}'".format(idx, resp.json()['result_code']))
            print("    Response: {}".format(resp.json()))
        else:
            print("{} success".format(idx))

