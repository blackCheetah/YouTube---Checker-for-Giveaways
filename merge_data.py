"""
    Merge authors and subscribers from different different channels (specific to channels) to one file
    and compare if subscribed people posted a comment

    # NamFlow [CZ/SK]                 -> UCPzd1WsihmmGowIlHEIHqxA
    # NamFlow - Herní Četa xD [CZ/SK] -> UC9uPfy9YSmOYk8ZXGBR2K6Q
"""

import os

def create_file(path, users):

    abs_path = os.path.abspath(path)
               
    with open(path, 'w', encoding='utf-8') as subs_file:
        subs_file.write(users)

    return f"\nUsers added to newly created file: \n -> {abs_path}\n"
    #print(f'Subscribers:\n {subs} \n -> added to {abs_path}\n')


def merge_files(first_file_path, second_file_path, output_file):
    
    channel_subscribers = []

    with open(first_file_path, 'r', encoding="utf8") as first_file_input:
        for line in first_file_input.read().splitlines():
            channel_subscribers.append(line)
    
    with open(second_file_path, 'r', encoding="utf8") as second_file_input:
        for i, line in enumerate(second_file_input.read().splitlines()):
            print(f"Comparing user number: [{i}], Username: ", line) 
            if line in channel_subscribers:
                print(f"User number: [{i}], Username: ", line, " is already in the list") 
                continue
            else:
                print(f"Appending user number: [{i}], Username: ", line) 
                channel_subscribers.append(line)

    subscribers_list = '\n'.join(channel_subscribers)
    print(create_file(output_file, subscribers_list))

def intersection_of_files(first_file_path, second_file_path, output_file):
    with open(first_file_path, 'r', encoding="utf8") as first_file_input:
        first_file_data = set(first_file_input.read().splitlines())

    with open(second_file_path, 'r', encoding="utf8") as second_file_input:
        second_file_data = set(second_file_input.read().splitlines())

    matched_users = first_file_data.intersection(second_file_data)
    print(create_file(output_file, '\n'.join(matched_users)))

if __name__ == '__main__':

    first_channel_id = 'UC9uPfy9YSmOYk8ZXGBR2K6Q' 
    second_channel_id = 'UCPzd1WsihmmGowIlHEIHqxA'
    merged_subscribers_file = 'merged_subscribers.txt'
    merged_authors_file = 'merged_authors.txt'
    merged_subs_and_authors_file = 'merged_subs_and_authors.txt'

    merge_files(
        f'output/{first_channel_id}-subscribers.txt', 
        f'output/{second_channel_id}-subscribers.txt',
        f"output/{merged_subscribers_file}"
    )

    merge_files(
        f'output/{first_channel_id}-authors.txt', 
        f'output/{second_channel_id}-authors.txt',
        f"output/{merged_authors_file}"
    )

    intersection_of_files(
        f'output/{merged_subscribers_file}',
        f'output/{merged_authors_file}',
        f'output/{merged_subs_and_authors_file}'
    )
