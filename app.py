import math
import json
import time
import httplib2
import os

from googleapiclient.discovery import build_from_document
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from __init__ import __version__, __author__, __created__, __description__
# General info about the program outputted to console
print(f"""
##################################################
# YouTube Checker for Giveaways [v{__version__}] 
# @author:      {__author__}   
# @description: {__description__}    
# @created:     {__created__}                    
# Usage example:                                 
# python app.py --channelid='<channel_id>'       
##################################################
"""
)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains

# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#     https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#     https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "config/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
     %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

def create_file_with_authors(path, authors):

    abs_path = os.path.abspath(path)
    authors_sepparated = '\n'.join(authors)
               
    with open(path, 'w', encoding='utf-8') as authors_file:
        authors_file.write(authors_sepparated)

    print(f'Authors {authors_sepparated} \n -> added to {abs_path}')

def create_file_with_subscribers(path, subs):

    abs_path = os.path.abspath(path)
               
    with open(path, 'w', encoding='utf-8') as subs_file:
        subs_file.write(subs)

    print(f'\nList of subscribers: \n {subs} \n -> added to {abs_path}\n')

def write_to_json(response, path):
    abs_path = os.path.abspath(path)

    with open(path, 'w', encoding='utf-8') as json_output:
        json.dump(response, json_output, indent=4)

    print(f'Data written to {abs_path}')

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs

# Authorize the request and store authorization credentials.
def get_authenticated_service(channel_id):
    """
        Authentication with Google Services
    """
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE, 
        scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE
    )

    storage = Storage(f"config/{channel_id}-oauth2.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    # Trusted testers can download this discovery document from the developers page
    # and it should be in the same directory with the code.
    with open("config/youtube-v3-discoverydocument.json", "r", encoding="utf8") as f:
        doc = f.read()
        return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


# Call the API's commentThreads.list method to list the existing comments.
def get_comments(youtube, video_id, channel_id):
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        channelId=channel_id,
        textFormat="plainText"
    ).execute()

    authors = []

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]

        if author not in authors:
            authors.append(author)

        print("Comment by %s: %s" % (author, text))

    return authors

# Source code (modified for my needs)
# https://stackoverflow.com/questions/37755678/retrieve-youtube-subscriptions-python-api#
def retrieve_youtube_subscriptions(channel_id):
    # In order to retrieve the YouTube subscriptions for the current user,
    # the user needs to authenticate and authorize access to their YouTube
    # subscriptions.
    youtube_authorization = get_authenticated_service(channel_id)

    list_of_subscribers = []

    try:
        # init
        next_page_token = ''
        subs_iteration = 0
        while True:
            # retrieve the YouTube subscriptions for the authorized user
            subscriptions_response = youtube_subscriptions(youtube_authorization, next_page_token, channel_id)
            subs_iteration += 1
            total_results = subscriptions_response['pageInfo']['totalResults']
            results_per_page = subscriptions_response['pageInfo']['resultsPerPage']
            total_iterations = math.ceil(total_results / results_per_page)
            total_in_percentage = round(subs_iteration / total_iterations * 100)
            print(f'Subscriptions iteration: {subs_iteration} of {total_iterations} ({total_in_percentage}%)')

            # get the token for the next page if there is one
            next_page_token = get_next_page(subscriptions_response)
            # extract the required subscription information
            subscribers = parse_youtube_subscriptions(subscriptions_response)
            #print("Channels:\n", channels, "\n")
            # add the channels relieved to the main channel list

            # Why reversed? Explanation here:
            # https://blender.stackexchange.com/questions/100850/remove-from-list-not-working-as-expected
            # https://stackoverflow.com/questions/6022764/python-removing-list-element-while-iterating-over-list
            for subscriber in reversed(subscribers):

                if subscriber in list_of_subscribers:
                    #print (f"Subscriber: {subscriber} is already in list of channels!")
                    subscribers.remove(subscriber)
                    #print (f"Removed subscriber: {subscriber} from the list.")
                    continue

            list_of_subscribers.extend(subscribers)

            if not next_page_token:
                break

        return list_of_subscribers
        
    except HttpError as err:
        print("An HTTP error {} occurred:\n{}".format(err.resp.status, err.content))


def get_next_page(subscriptions_response):
    # check if the subscription response contains a reference to the
    # next page or not
    if 'nextPageToken' in subscriptions_response:
        next_page_token = subscriptions_response['nextPageToken']
    else:
        next_page_token = ''
    return next_page_token

def parse_youtube_subscriptions(subscriptions_response):
    subscribers_list = []
    for item in subscriptions_response["items"]:
        subscribers_list.append(item["subscriberSnippet"]["title"])

    #subscribers_formatted = '\n'.join(subscribers_list)
    #print(f"Subscribers {subscribers_formatted}")

    return subscribers_list

def youtube_subscriptions(youtube, next_page_token, channel_id):
    results = youtube.subscriptions().list(
        part="subscriberSnippet",
        #channelId=channel_id,
        mySubscribers=True,
        #mine=True,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    return results

def search_list_mine(client, channel_id, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.search().list(
    **kwargs
    ).execute()

    return write_to_json(response, f'output/{channel_id}-videos.json')

def get_yt_video_ids(path_to_videos):

    video_ids_list = []

    try:
        with open(path_to_videos, 'r') as input_json_file:
            loaded_json = json.load(input_json_file)

        for i in range(0, len(loaded_json['items'])):
            video_ids_list.append(loaded_json['items'][i]['id']['videoId'])

            #print(loaded_json['items'][i]['id']['videoId'])
            #print(loaded_json['items'][i]['snippet']['title'])
            #print("\n")

    except FileNotFoundError as e:
        print(f"File not found due following error:\n{e}")

    return video_ids_list


if __name__ == "__main__":

    # The "channelid" option specifies the YouTube channel ID that uniquely
    # identifies the channel for which the comment will be inserted.
    argparser.add_argument(
        "--channelid",
        help="Required; ID for channel for which the comment will be inserted."
    )

    args = argparser.parse_args()

    # Manual values for arguments
    # NamFlow [CZ/SK]                 -> UCPzd1WsihmmGowIlHEIHqxA
    # NamFlow - Herní Četa xD [CZ/SK] -> UC9uPfy9YSmOYk8ZXGBR2K6Q
    # args.channelid = "UCPzd1WsihmmGowIlHEIHqxA"

    if not args.channelid:
        exit("Please specify channelid using the --channelid= parameter.")

    # Authentication
    youtube = get_authenticated_service(args.channelid)

    # Complete list with people who commented on videos
    authors_complete_list = []
    subscribers_list = []

    try:
        # Data can be accessed through this link as well
        # https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&maxResults=50&order=date&type=video&key={API_KEY}

        # Get video IDs of last 50 videos
        search_list_mine(
            youtube,
            args.channelid,
            part='snippet',
            maxResults=50,
            forMine=True,
            type='video'
        )

        video_ids_list = get_yt_video_ids(f'output/{args.channelid}-videos.json')

        # Get comments from up to 50 videos
        for video_id in video_ids_list:
            time.sleep(1)

            authors = get_comments(youtube, video_id, None)

            for author in authors:
                if author in authors_complete_list:
                    continue
                else:
                    authors_complete_list.append(author)
        
        create_file_with_authors(f'output/{args.channelid}-authors.txt', authors_complete_list)

        # Retrieve list of subscribers
        print('Gather list of subscribers')
        all_channels = retrieve_youtube_subscriptions(args.channelid)
        all_channels_formatted = "\n".join(all_channels)
        print('Subscriptions complete')
        print('Subscriptions found: {}'.format(len(all_channels)))

        create_file_with_subscribers(f'output/{args.channelid}-subscribers.txt', all_channels_formatted)
        

    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    else:
        print("All subscribers and comments with unique authors gathered!")
