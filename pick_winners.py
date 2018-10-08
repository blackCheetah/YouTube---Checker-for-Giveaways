import random
from datetime import datetime
import os
import json

def load_file_data(file_path):

    potential_winners = {}

    with open(file_path,'r', encoding="utf8") as file_path_input:
        for line_num, winner in enumerate(file_path_input):
            potential_winners[line_num] = winner

    return potential_winners

def create_file(path, users):

    abs_path = os.path.abspath(path)
               
    with open(path, 'w', encoding='utf-8') as output_file:
        output_file.write(users)

    return f"\nWinners added to newly created file: \n -> {abs_path}\n"
    #print(f'Subscribers:\n {subs} \n -> added to {abs_path}\n')


if __name__ == '__main__':

    people = load_file_data('output/merged_subs_and_authors.txt')
    rewards = load_file_data('input/rewards.txt')
    
    num_of_people = len(people)
    num_of_rewards = len(rewards)
    print(f"Number of potential winners: {num_of_people}")
    print(f"Number of rewards: {num_of_rewards}")

    random.seed(datetime.now())

    final_winners_numbers = []

    for winner_number in range(0, num_of_rewards):
        final_winners_numbers.append(random.randint(0, num_of_people))

    list_of_winners = {}

    # for num in final_winners_numbers:
    #     winner_name = people[num]
    #     winner_num = people[winner_name]

    for number, person in people.items():

        if number in final_winners_numbers:
            print(f" Winner Winner Chicken Dinner!: {number}: {person}")
            list_of_winners[number] = person
        else:
            continue

    create_file('output/winners.txt', json.dumps(list_of_winners, indent=4))
    

        

