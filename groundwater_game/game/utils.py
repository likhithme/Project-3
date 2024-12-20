# from game.models import Option, GameResult
# import random

# def decide_next_question(user, current_question, selected_option_id, alpha=0.1, gamma=0.9):
#     # Fetch the selected option
#     selected_option = Option.objects.get(id=selected_option_id)

#     # Reward is based on the option's points
#     reward = selected_option.points

#     # Fetch or simulate the next question based on the option's next_question
#     next_question = selected_option.next_question

#     # Log the user's progress in GameResult
#     game_result, created = GameResult.objects.get_or_create(
#         user=user,
#         scenario=current_question.scenario,
#         defaults={"score": 0, "total_questions": 0},
#     )
    
#     # Update the Q-value (Q-learning formula: Q(s, a) = Q(s, a) + α * (reward + γ * max_a Q(s', a') - Q(s, a)))
#     current_q_value = game_result.score  # Assuming this is the current Q-value (you can store it separately if needed)
#     max_q_value = reward + gamma * current_q_value  # For simplicity, using the reward as the max Q-value for now

#     # Update the game result score (you can track more details as needed)
#     game_result.score += reward
#     game_result.total_questions += 1
#     game_result.save()

#     # Determine the next difficulty level
#     current_difficulty = current_question.difficulty  # Assuming this is a string field with 'easy', 'medium', 'difficult'

#     # Adjust difficulty based on correctness of the answer
#     if selected_option.is_correct:
#         # Increase difficulty (but not beyond 'difficult')
#         if current_difficulty == 'easy':
#             next_difficulty = 'medium'
#         elif current_difficulty == 'medium':
#             next_difficulty = 'difficult'
#         else:
#             next_difficulty = 'difficult'  # Stay at 'difficult' if already there
#     else:
#         # Decrease difficulty (but not below 'easy')
#         if current_difficulty == 'difficult':
#             next_difficulty = 'medium'
#         elif current_difficulty == 'medium':
#             next_difficulty = 'easy'
#         else:
#             next_difficulty = 'easy'  # Stay at 'easy' if already there

#     # Select the next question with the new difficulty level
#     next_question = None
#     if next_difficulty:
#         # Filter the questions by the new difficulty level
#         possible_next_questions = current_question.scenario.questions.filter(difficulty=next_difficulty)
#         if possible_next_questions.exists():
#             next_question = random.choice(possible_next_questions)  # Randomly select one of the possible next questions

#     return next_question


from game.models import Option
import random

def decide_next_question(user, current_question, selected_option_id, selected_question_ids, alpha=0.1, gamma=0.9):
    """
    Determines the next question based on the user's performance.

    Args:
        user: The current user.
        current_question: The current question being answered.
        selected_option_id: The ID of the selected option.
        selected_question_ids: List of question IDs already attempted by the user.
        alpha: Learning rate (for potential Q-learning expansion).
        gamma: Discount factor (for potential Q-learning expansion).

    Returns:
        The next question object or None if no valid question is found.
    """
    # Fetch the selected option
    selected_option = Option.objects.get(id=selected_option_id)

    # Reward based on the option's points
    reward = selected_option.points

    # Determine the next difficulty based on the current question and correctness
    current_difficulty = current_question.difficulty
    next_difficulty = {
        'easy': 'medium' if selected_option.is_correct else 'easy',
        'medium': 'difficult' if selected_option.is_correct else 'easy',
        'difficult': 'difficult' if selected_option.is_correct else 'medium',
    }[current_difficulty]

    # Fetch possible next questions based on the new difficulty, excluding already attempted questions
    possible_next_questions = current_question.scenario.questions.filter(
        difficulty=next_difficulty
    ).exclude(id__in=selected_question_ids)

    # Select a random question if available
    if possible_next_questions.exists():
        return random.choice(possible_next_questions)

    # If no questions are available at the desired difficulty, try any remaining questions
    remaining_questions = current_question.scenario.questions.exclude(
        id__in=selected_question_ids
    )
    if remaining_questions.exists():
        return random.choice(remaining_questions)

    # If no questions are available, return None
    return None

