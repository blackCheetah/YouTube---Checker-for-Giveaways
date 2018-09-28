"""
    Extract youtube video IDs from json file and append it to text file
"""
import json
import os
from pprint import pprint

def get_yt_video_ids(path):
    with open(path, 'r') as input_json_file:
        data = json.load(input_json_file)

    return data


if __name__ == '__main__':

    path_to_videos = 'output/videos.json'
    loaded_json = get_yt_video_ids(path_to_videos)

    for i in range(0, len(loaded_json['items'])):
        print(loaded_json['items'][i]['id']['videoId'])
        print(loaded_json['items'][i]['snippet']['title'])
        print("\n")
