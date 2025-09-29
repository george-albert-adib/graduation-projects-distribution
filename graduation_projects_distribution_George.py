# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 22:50:10 2025

@author: George Albert
"""

import itertools
import csv
import pandas as pd


def distribute_items(users, items, preferences):
    """
    Distributes items to users based on scores and preferences.

    Args:
        users (dict): A dictionary where keys are user IDs and values are scores.
        items (dict): A dictionary where keys are item IDs and values are their available stock.
        preferences (dict): A nested dictionary where keys are user IDs. The values are
                          dictionaries mapping item IDs to their preference rank (1-based).

    Returns:
        dict: A dictionary mapping user IDs to their assigned item ID.
    """
    # Sort users by score in descending order
    sorted_users = users.sort_values(by='score', ascending=False)
    assignments = pd.DataFrame(columns=["user_id","score","project_id","preference_rank", "previous_preferences"], index=range(len(users)))
    item_stock = items.copy()  # Use a copy to avoid modifying the original data

    print("--- Initial Distribution Process ---")
    counter = 0
    for index, row in sorted_users.iterrows():
        user_id, score = row
        print(f"Assigning item for user '{user_id}' (Score: {score})")
        # Find the first preferred item that is still in stock
        # Sort preferences by rank to check in the correct order
        user_prefs = preferences.loc[preferences['user_id']==user_id]
        single_suer_prefs = user_prefs.drop(columns=['user_id'])
        
        assigned = False
        previous_prefs = list()
        for rank, item_id in single_suer_prefs.items():
            item_id = int(item_id.values[0])
            if item_stock.loc[item_stock['project_id']==item_id, "capacity"].values[0] > 0:
                # assignments[user_id] = item_id, score, rank, previous_prefs
                assignments.loc[counter] = pd.Series({"user_id":user_id, "score":score, "project_id":item_id, "preference_rank":rank, "previous_preferences":previous_prefs})
                counter += 1
                item_stock.loc[item_stock['project_id']==item_id, "capacity"] -= 1
                print(f"  -> Assigned item '{item_id}' (Rank: {rank})")
                assigned = True
                break
            previous_prefs.append(item_id)
        if not assigned:
            print(f"  -> No item could be assigned for user '{user_id}'.")

    return assignments

def calculate_total_satisfaction(assignments, preferences):
    """
    Calculates the total satisfaction score based on assignments and preferences.

    Args:
        assignments (dict): A dictionary mapping user IDs to assigned item IDs.
        preferences (dict): The original preferences data.

    Returns:
        int: The sum of all assigned item ranks. Lower is better.
    """
    total_score = 0
    for user_id, item_id in assignments.items():
        rank = preferences[user_id].get(item_id, float('inf'))
        total_score += rank
    return total_score

def find_optimal_swap(assignments, users, preferences):
    """
    Finds a preference swap between two users that maximizes overall satisfaction.

    Args:
        assignments (dict): The current item assignments.
        users (dict): The user scores.
        preferences (dict): The original preferences data.

    Returns:
        tuple: A tuple containing the two users to swap, and the change in satisfaction.
               Returns (None, None, 0) if no beneficial swap is found.
    """
    sorted_users = sorted(users.keys())  # Sort keys for consistent pairing
    user_pairs = itertools.combinations(sorted_users, 2)
    best_swap = None
    max_improvement = 0

    print("\n--- Finding Optimal Swap ---")
    for user1, user2 in user_pairs:
        item1 = assignments.get(user1)
        item2 = assignments.get(user2)

        if not item1 or not item2:
            continue  # Both users must have an item assigned

        # Calculate current satisfaction for the pair
        current_satisfaction = preferences[user1].get(item1, float('inf')) + \
                               preferences[user2].get(item2, float('inf'))

        # Calculate satisfaction if they were to swap
        swapped_satisfaction = preferences[user1].get(item2, float('inf')) + \
                               preferences[user2].get(item1, float('inf'))

        improvement = current_satisfaction - swapped_satisfaction

        if improvement > max_improvement:
            max_improvement = improvement
            best_swap = (user1, user2)

    return best_swap, max_improvement

def main():
    """
    Main function to run the item distribution and optimization process.
    """
    # Define file paths
    users_filepath = 'users.csv'
    items_filepath = 'Items.csv'
    preferences_filepath = 'Preferences.csv'

    # Read data from CSV files
    users_pd = pd.read_csv(users_filepath)
    items_pd = pd.read_csv(items_filepath)
    preferences_pd = pd.read_csv(preferences_filepath)
    # users = read_users_from_csv(users_filepath)
    # items = read_items_from_csv(items_filepath)
    # preferences = read_preferences_from_csv(preferences_filepath)

    if users_pd is None or items_pd is None or preferences_pd is None:
        print("Exiting due to file read errors.")
        return

    # Phase 1: Initial Distribution
    initial_assignments = distribute_items(users_pd, items_pd, preferences_pd)
    # print(initial_assignments)
    initial_assignments.to_csv("Initial_distribution v3 2.csv")
    
    grouped_df = initial_assignments.groupby('project_id')['user_id']
    groups_lists = pd.DataFrame(columns=["project_id","users"], index=range(len(items_pd)))
    counter = 0
    for key, item in grouped_df:
        # print(grouped_df.get_group(key), "\n\n")
        groups_lists.loc[counter] = pd.Series({"project_id":key, "users":list(grouped_df.get_group(key))})
        counter += 1
        
    groups_lists.to_csv("groups lists v3.csv")
    print(initial_assignments.groupby('project_id')['score'].mean())
    # print(initial_assignments.groupby(by="project_id"))
    
    # initial_satisfaction = calculate_total_satisfaction(initial_assignments, preferences)
"""    
    assignments_df = pd.DataFrame(columns=["user_ID","project_code","priority","score"], index=range(len(initial_assignments)))
    print("\n--- Initial Assignments ---")
    counter = 0
    for user, item in initial_assignments.items():
        rank = preferences[user].get(item)
        print(f"User '{user}' gets '{item}' (Rank: {rank})")
        score_temp = users[user]
        assignments_df.iloc[counter] = pd.Series({'user_ID':user, 'project_code':item, 'priority':rank, "score":score_temp})
        # assignments_df.iloc[counter,"project_code"] = item
        # assignments_df.iloc[counter,"priority"] = rank
        counter += 1

    print(f"\nInitial Total Satisfaction Score: {initial_satisfaction}")

    # csv_filename = "first_distribution.csv"
    # assignments_df = pd.DataFrame(initial_assignments, index=[0,1])
    assignments_df.to_csv('first_distribution.csv', index=False)
        
    # Phase 2: Find Optimal Swap
    swap_suggestion, improvement = find_optimal_swap(initial_assignments, users, preferences)

    if swap_suggestion:
        user1, user2 = swap_suggestion
        print(f"Suggestion: Swap items between '{user1}' and '{user2}'.")
        print(f"This swap would improve the total satisfaction score by {improvement}.")
        
        # Simulate the swap and show the new assignments
        new_assignments = initial_assignments.copy()
        new_assignments[user1], new_assignments[user2] = new_assignments[user2], new_assignments[user1]
        
        new_satisfaction = calculate_total_satisfaction(new_assignments, preferences)
        print(f"New Total Satisfaction Score after swap: {new_satisfaction}")

    else:
        print("No beneficial swap was found to improve overall satisfaction.")
"""
if __name__ == "__main__":
    main()