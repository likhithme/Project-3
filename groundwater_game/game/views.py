import random
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Scenario

def home(request):
    return render(request, 'game/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user with the provided username
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'game/register.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomLoginForm

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')  # Redirect to the profile page
        else:
            form.add_error(None, "Invalid username or password")
    else:
        form = CustomLoginForm()
    return render(request, 'game/login.html', {'form': form})

    
from django.db.models import Max, Sum, Count, Prefetch
from django.shortcuts import render
from .models import Scenario, GameResult

def profile(request):
    user = request.user
    age = user.age

    # Determine the age category
    if age < 12:
        category = 'kids'
    elif 12 <= age < 18:
        category = 'teens'
    else:
        category = 'adults'

    # Fetch scenarios for the user
    scenarios = Scenario.objects.filter(category=category)

    # Prefetch related objects for optimization
    results = GameResult.objects.filter(user=user).select_related('scenario').prefetch_related(
        Prefetch(
            'scenario__questions',
            to_attr='prefetched_questions'
        )
    )

    # Add total_possible_score to game results
    game_results = []
    for result in results:
        total_possible_score = sum(
            question.option_set.order_by('-points').first().points
            for question in result.scenario.prefetched_questions
        )
        game_results.append({
            'scenario': result.scenario,
            'score': result.score,
            'total_possible_score': total_possible_score,
        })

    # Leaderboard logic
    scenario_filter = request.GET.get('scenario')  # Get scenario filter from query params
    leaderboard = GameResult.objects.select_related('scenario', 'user')

    if scenario_filter:
        leaderboard = leaderboard.filter(scenario_id=scenario_filter)

    leaderboard = leaderboard.values(
        'user__username',
        'scenario__title'  # Include scenario title
    ).annotate(
        total_score=Sum('score'),
        games_played=Count('scenario')
    ).order_by('-total_score')

    return render(request, 'game/profile.html', {
        'user': user,
        'scenarios': scenarios,
        'game_results': game_results,
        'leaderboard': leaderboard,
        'scenario_filter': scenario_filter,
        'all_scenarios': Scenario.objects.all(),
    })



# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Scenario, GameResult
# import random

# def scenario_question_view(request, scenario_id, question_index=0):
#     # Get the scenario object
#     scenario = get_object_or_404(Scenario, id=scenario_id)

#     # Retrieve and shuffle questions only once per game session
#     if 'question_order' not in request.session:
#         questions = list(scenario.questions.all())
#         random.shuffle(questions)
#         request.session['question_order'] = [q.id for q in questions]
#     else:
#         questions = [get_object_or_404(scenario.questions, id=q_id) for q_id in request.session['question_order']]

#     # Calculate total possible score once
#     if 'total_possible_score' not in request.session:
#         request.session['total_possible_score'] = sum(
#             max(question.options.all(), key=lambda option: option.points).points
#             for question in questions
#         )

#     total_possible_score = request.session['total_possible_score']

#     # Check if all questions have been answered
#     if question_index >= len(questions):
#         # Calculate the total score
#         score = sum(
#             request.session.get(f'question_{question.id}_points', 0)
#             for question in questions
#         )

#         # Save the game result
#         GameResult.objects.create(
#             user=request.user,
#             scenario=scenario,
#             score=score,
#             total_questions=len(questions),
#         )

#         # Clear session data
#         request.session.pop('question_order', None)
#         request.session.pop('total_possible_score', None)
#         for question in questions:
#             request.session.pop(f'question_{question.id}_points', None)

#         return redirect('game_complete', scenario_id=scenario_id)

#     # Get the current question
#     current_question = questions[question_index]

#     # Shuffle the options for the current question
#     options = list(current_question.options.all())
#     random.shuffle(options)

#     # Handle form submission
#     if request.method == 'POST':
#         selected_option_id = request.POST.get('option')

#         # If an option is selected, save the points for the question in the session
#         selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)
#         if selected_option:
#             request.session[f'question_{current_question.id}_points'] = selected_option.points

#         # Redirect to the next question
#         return redirect('scenario_question', scenario_id=scenario_id, question_index=question_index + 1)

#     # Render the question template
#     return render(request, 'game/scenario_question.html', {
#         'scenario': scenario,
#         'current_question': current_question,
#         'options': options,
#         'current_question_number': question_index + 1,
#         'total_questions': len(questions),
#         'total_possible_score': total_possible_score,
#     })



# from django.shortcuts import render, get_object_or_404
# from .models import Scenario, GameResult

# def game_complete_view(request, scenario_id):
#     scenario = get_object_or_404(Scenario, id=scenario_id)

#     # Fetch the most recent result for this scenario
#     result = GameResult.objects.filter(user=request.user, scenario=scenario).last()

#     if not result:
#         return redirect('profile')

#     # Fetch selected question IDs from the session
#     session_prefix = f"scenario_{scenario_id}_game_"
#     selected_question_ids = request.session.get(session_prefix + 'selected_questions', [])

#     # Debugging log
#     print(f"Selected Question IDs in session: {selected_question_ids}")

#     # Initialize total_possible_score
#     total_possible_score = 0

#     # Calculate the total possible score for the 10 selected questions
#     if selected_question_ids:
#         questions = scenario.questions.filter(id__in=selected_question_ids)
#         total_possible_score = 0  # Initialize the total score to 0
#         for question in questions:
#             # Check if the question has any options
#             if question.option_set.exists():
#                 # Get the option with the highest points for the question
#                 max_option = max(question.option_set.all(), key=lambda option: option.points, default=None)
#                 if max_option:  # Ensure that max_option is not None
#                     total_possible_score += max_option.points

#     # Now total_possible_score will contain the sum of the maximum points for each question


#     # Debugging log
#     print(f"Total Possible Score: {total_possible_score}")

#     return render(request, 'game/game_complete.html', {
#         'scenario': scenario,
#         'score': result.score,
#         'total_questions': result.total_questions,
#         'total_possible_score': total_possible_score,
#     })


def game_complete_view(request, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id)

    # Fetch the most recent result for this scenario
    result = GameResult.objects.filter(user=request.user, scenario=scenario).last()

    if not result:
        return redirect('profile')

    # Fetch selected question IDs from the session
    session_prefix = f"scenario_{scenario_id}_game_"
    selected_question_ids = request.session.get(session_prefix + 'selected_questions', [])

    # Debugging log
    print(f"Selected Question IDs in session: {selected_question_ids}")

    # Initialize total_possible_score
    total_possible_score = 0

    # Calculate the total possible score for the 10 selected questions
    if selected_question_ids:
        questions = scenario.questions.filter(id__in=selected_question_ids)
        total_possible_score = sum(
            max(
                question.option_set.all(),
                key=lambda option: option.points,
                default=None  # Handle cases where no options exist
            ).points
            for question in questions if question.option_set.exists()
        )

    # Debugging log
    print(f"Total Possible Score: {total_possible_score}")

    # Clear session data after game completion
    for key in list(request.session.keys()):
        if key.startswith(session_prefix):
            del request.session[key]

    return render(request, 'game/game_complete.html', {
        'scenario': scenario,
        'score': result.score,
        'total_questions': result.total_questions,
        'total_possible_score': total_possible_score,
    })




# game_results_view

# from django.shortcuts import render
# from .models import GameResult, Scenario

# def game_results_view(request):
#     user = request.user

#     # Fetch all game results for the user
#     game_results = GameResult.objects.filter(user=user).select_related('scenario')

#     # Calculate total possible score for each scenario
#     results_with_possible_scores = []
#     for result in game_results:
#         total_possible_score = sum(
#             max(question.option_set.all(), key=lambda option: option.points).points
#             for question in result.scenario.questions.all()
#         )
#         results_with_possible_scores.append({
#             'scenario': result.scenario.title,
#             'score': result.score,
#             'total_possible_score': 60
#         })

#     return render(request, 'game/game_results.html', {
#         'results_with_possible_scores': results_with_possible_scores
#     })


# views.py
from django.shortcuts import render
from .models import GameResult, Scenario

def game_results_view(request):
    user = request.user

    # Fetch all game results for the user, ordered by most recent first
    game_results = GameResult.objects.filter(user=user).select_related('scenario').order_by('-id')

    # Calculate total possible score for each scenario
    results_with_possible_scores = []
    for result in game_results:
        total_possible_score = sum(
            max(question.option_set.all(), key=lambda option: option.points).points
            for question in result.scenario.questions.all()
        )
        results_with_possible_scores.append({
            'scenario': result.scenario.title,
            'score': result.score,
            'total_possible_score': 60  # Or calculate based on the scenario
        })

    return render(request, 'game/game_results.html', {
        'results_with_possible_scores': results_with_possible_scores
    })


# leaderboard view

from django.db.models import Sum, Count
from django.shortcuts import render
from .models import GameResult

def leaderboard(request):
    scenario_filter = request.GET.get('scenario')  # Get scenario filter from query params
    leaderboard = GameResult.objects.select_related('scenario', 'user')

    if scenario_filter:
        leaderboard = leaderboard.filter(scenario_id=scenario_filter)

    leaderboard = leaderboard.values(
        'user__username',
        'scenario__title'  # Include scenario title
    ).annotate(
        total_score=Sum('score'),
        games_played=Count('scenario')
    ).order_by('-total_score')

    return render(request, 'game/leaderboard.html', {
        'leaderboard': leaderboard,
        'scenario_filter': scenario_filter,
        'all_scenarios': Scenario.objects.all(),
    })


# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Scenario, GameResult, Option
# from game.utils import decide_next_question  # Import the Q-learning function
# import random

# def scenario_question_view(request, scenario_id, question_index=0):
#     scenario = get_object_or_404(Scenario, id=scenario_id)

#     # Unique session keys per scenario
#     session_prefix = f"scenario_{scenario_id}_"

#     # Retrieve and shuffle questions only once per scenario
#     if session_prefix + 'question_order' not in request.session:
#         questions = list(scenario.questions.all())
#         random.shuffle(questions)
#         request.session[session_prefix + 'question_order'] = [q.id for q in questions]
#     else:
#         questions = [
#             get_object_or_404(scenario.questions, id=q_id)
#             for q_id in request.session[session_prefix + 'question_order']
#         ]

#     # Calculate total possible score once
#     if session_prefix + 'total_possible_score' not in request.session:
#         request.session[session_prefix + 'total_possible_score'] = sum(
#             max(question.option_set.all(), key=lambda option: option.points).points
#             for question in questions
#         )

#     total_possible_score = request.session[session_prefix + 'total_possible_score']

#     # Check if all questions have been answered
#     if question_index >= len(questions):
#         # Calculate the total score
#         score = sum(
#             request.session.get(f"{session_prefix}question_{question.id}_points", 0)
#             for question in questions
#         )

#         # Save the game result
#         GameResult.objects.create(
#             user=request.user,
#             scenario=scenario,
#             score=score,
#             total_questions=len(questions),
#         )

#         # Clear session data for this scenario
#         request.session.pop(session_prefix + 'question_order', None)
#         request.session.pop(session_prefix + 'total_possible_score', None)
#         for question in questions:
#             request.session.pop(f"{session_prefix}question_{question.id}_points", None)
#             request.session.pop(f"{session_prefix}question_{question.id}_options_order", None)

#         return redirect('game_complete', scenario_id=scenario_id)

#     # Get the current question
#     current_question = questions[question_index]

#     # Preserve the order of options for this question
#     if f"{session_prefix}question_{current_question.id}_options_order" not in request.session:
#         options = list(current_question.option_set.all())
#         random.shuffle(options)
#         request.session[f"{session_prefix}question_{current_question.id}_options_order"] = [option.id for option in options]
#     else:
#         option_ids = request.session[f"{session_prefix}question_{current_question.id}_options_order"]
#         options = [get_object_or_404(current_question.option_set, id=opt_id) for opt_id in option_ids]

#     # Initialize feedback variables
#     feedback = None
#     selected_option_id = None
#     correct_option_id = None

#     # Handle form submission
#     if request.method == 'POST':
#         selected_option_id = request.POST.get('option')

#         # If an option is selected, save the selected option's points to the session
#         selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)
#         if selected_option:
#             correct_option = next((opt for opt in options if opt.is_correct), None)
#             correct_option_id = correct_option.id if correct_option else None

#             if selected_option.is_correct:
#                 feedback = {
#                     'correct': True,
#                     'points': selected_option.points,
#                     'selected_option_id': selected_option.id,
#                 }
#             else:
#                 feedback = {
#                     'correct': False,
#                     'points': selected_option.points,
#                     'selected_option_id': selected_option.id,
#                 }

#             # Store points in session for scoring
#             request.session[f"{session_prefix}question_{current_question.id}_points"] = selected_option.points

#             # Use the Q-learning function to decide the next question
#             next_question = decide_next_question(request.user, current_question, selected_option.id)

#             # Redirect to the next question based on the Q-learning result
#             if next_question:
#                 next_question_index = questions.index(next_question)
#                 return redirect('scenario_question', scenario_id=scenario_id, question_index=next_question_index)
#             else:
#                 return redirect('game_complete', scenario_id=scenario_id)

#     # Render the question template
#     return render(request, 'game/scenario_question.html', {
#         'scenario': scenario,
#         'current_question': current_question,
#         'options': options,
#         'current_question_number': question_index + 1,
#         'total_questions': len(questions),
#         'total_possible_score': total_possible_score,
#         'feedback': feedback,
#         'selected_option_id': selected_option_id,
#         'correct_option_id': correct_option_id,
#         'question_index': question_index,  # Needed for the template's "Next Question" button
#     })



# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Scenario, GameResult, Option
# from game.utils import decide_next_question  # Import the Q-learning function
# import random

# def scenario_question_view(request, scenario_id, question_index=0):
#     scenario = get_object_or_404(Scenario, id=scenario_id)
#     session_prefix = f"scenario_{scenario_id}_game_"

#     # Load session data
#     selected_question_ids = request.session.get(session_prefix + 'selected_questions', [])
#     total_score = request.session.get(session_prefix + 'total_score', 0)
#     game_result_id = request.session.get(session_prefix + 'game_result_id')

#     # If no game result exists in the session, create a new one
#     if not game_result_id:
#         game_result = GameResult.objects.create(user=request.user, scenario=scenario, score=0, total_questions=0)
#         request.session[session_prefix + 'game_result_id'] = game_result.id
#     else:
#         try:
#             game_result = GameResult.objects.get(id=game_result_id)
#         except GameResult.DoesNotExist:
#             return redirect('error')  # Redirect to an error page if necessary

#     # Initialize the game if no questions have been selected yet
#     if not selected_question_ids:
#         initial_questions = scenario.questions.filter(difficulty='easy')
#         if initial_questions.exists():
#             first_question = random.choice(initial_questions)
#             selected_question_ids = [first_question.id]
#             request.session[session_prefix + 'selected_questions'] = selected_question_ids
#         else:
#             return render(request, 'game/error.html', {'message': 'No questions available for this scenario.'})

#     # Check if the game is complete
#     if question_index >= len(selected_question_ids):
#         if len(selected_question_ids) >= 10:
#             game_result.score = total_score
#             game_result.total_questions = len(selected_question_ids)
#             game_result.save()

#             # Clear session data after game completion
#             for key in list(request.session.keys()):
#                 if key.startswith(session_prefix):
#                     del request.session[key]

#             return redirect('game_complete', scenario_id=scenario_id)

#         return redirect('scenario_question', scenario_id=scenario_id, question_index=0)

#     # Get the current question
#     current_question_id = selected_question_ids[question_index]
#     current_question = get_object_or_404(scenario.questions, id=current_question_id)

#     # Shuffle and store options in session to ensure randomness
#     if f"{session_prefix}question_{current_question.id}_options_order" not in request.session:
#         options = list(current_question.option_set.all())
#         random.shuffle(options)
#         request.session[f"{session_prefix}question_{current_question.id}_options_order"] = [option.id for option in options]
#     else:
#         option_ids = request.session[f"{session_prefix}question_{current_question.id}_options_order"]
#         options = [get_object_or_404(current_question.option_set, id=opt_id) for opt_id in option_ids]

#     # Handle form submission
#     if request.method == 'POST':
#         selected_option_id = request.POST.get('option')
#         selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)

#         if selected_option and selected_option.is_correct:
#             total_score += selected_option.points

#         request.session[session_prefix + 'total_score'] = total_score

#         # Decide next question
#         if len(selected_question_ids) < 10:
#             next_question = decide_next_question(
#                 request.user,
#                 current_question,
#                 selected_option_id,
#                 selected_question_ids
#             )

#             # Ensure next question is unique
#             while next_question and next_question.id in selected_question_ids:
#                 next_question = decide_next_question(
#                     request.user,
#                     current_question,
#                     selected_option_id,
#                     selected_question_ids
#                 )

#             if next_question:
#                 selected_question_ids.append(next_question.id)
#                 request.session[session_prefix + 'selected_questions'] = selected_question_ids

#         # Redirect to the next question
#         return redirect('scenario_question', scenario_id=scenario_id, question_index=question_index + 1)

#     return render(request, 'game/scenario_question.html', {
#         'scenario': scenario,
#         'current_question': current_question,
#         'options': options,
#         'current_question_number': question_index + 1,
#         'total_questions': 10,
#     })

#best_version

# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Scenario, GameResult, Option
# from game.utils import decide_next_question  # Import the Q-learning function
# import random

# def scenario_question_view(request, scenario_id, question_index=0):
#     scenario = get_object_or_404(Scenario, id=scenario_id)
#     session_prefix = f"scenario_{scenario_id}_game_"

#     # Load session data
#     selected_question_ids = request.session.get(session_prefix + 'selected_questions', [])
#     total_score = request.session.get(session_prefix + 'total_score', 0)
#     game_result_id = request.session.get(session_prefix + 'game_result_id')

#     # If no game result exists in the session, create a new one
#     if not game_result_id:
#         game_result = GameResult.objects.create(user=request.user, scenario=scenario, score=0, total_questions=0)
#         request.session[session_prefix + 'game_result_id'] = game_result.id
#     else:
#         try:
#             game_result = GameResult.objects.get(id=game_result_id)
#         except GameResult.DoesNotExist:
#             return redirect('error')  # Redirect to an error page if necessary

#     # Initialize the game if no questions have been selected yet
#     if not selected_question_ids:
#         initial_questions = scenario.questions.filter(difficulty='easy')
#         if initial_questions.exists():
#             first_question = random.choice(initial_questions)
#             selected_question_ids = [first_question.id]
#             request.session[session_prefix + 'selected_questions'] = selected_question_ids
#         else:
#             return render(request, 'game/error.html', {'message': 'No questions available for this scenario.'})

#     # Check if the game is complete
#     if question_index >= len(selected_question_ids):
#         if len(selected_question_ids) >= 10:
#             game_result.score = total_score
#             game_result.total_questions = len(selected_question_ids)
#             game_result.save()

#             return redirect('game_complete', scenario_id=scenario_id)

#         return redirect('scenario_question', scenario_id=scenario_id, question_index=0)

#     # Get the current question
#     current_question_id = selected_question_ids[question_index]
#     current_question = get_object_or_404(scenario.questions, id=current_question_id)

#     # Shuffle and store options in session to ensure randomness
#     if f"{session_prefix}question_{current_question.id}_options_order" not in request.session:
#         options = list(current_question.option_set.all())
#         random.shuffle(options)
#         request.session[f"{session_prefix}question_{current_question.id}_options_order"] = [option.id for option in options]
#     else:
#         option_ids = request.session[f"{session_prefix}question_{current_question.id}_options_order"]
#         options = [get_object_or_404(current_question.option_set, id=opt_id) for opt_id in option_ids]

#     # Handle form submission
#     if request.method == 'POST':
#         selected_option_id = request.POST.get('option')
#         selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)

#         if selected_option and selected_option.is_correct:
#             total_score += selected_option.points

#         request.session[session_prefix + 'total_score'] = total_score

#         # Decide next question
#         if len(selected_question_ids) < 10:
#             next_question = decide_next_question(
#                 request.user,
#                 current_question,
#                 selected_option_id,
#                 selected_question_ids
#             )

#             # Ensure next question is unique
#             while next_question and next_question.id in selected_question_ids:
#                 next_question = decide_next_question(
#                     request.user,
#                     current_question,
#                     selected_option_id,
#                     selected_question_ids
#                 )

#             if next_question:
#                 selected_question_ids.append(next_question.id)
#                 request.session[session_prefix + 'selected_questions'] = selected_question_ids

#         # Redirect to the next question
#         return redirect('scenario_question', scenario_id=scenario_id, question_index=question_index + 1)

#     return render(request, 'game/scenario_question.html', {
#         'scenario': scenario,
#         'current_question': current_question,
#         'options': options,
#         'current_question_number': question_index + 1,
#         'total_questions': 10,
#     })



from django.shortcuts import render, redirect, get_object_or_404
from .models import Scenario, GameResult, Option
from game.utils import decide_next_question
import random

def scenario_question_view(request, scenario_id, question_index=0):
    scenario = get_object_or_404(Scenario, id=scenario_id)
    session_prefix = f"scenario_{scenario_id}_game_"

    # Load session data
    selected_question_ids = request.session.get(session_prefix + 'selected_questions', [])
    total_score = request.session.get(session_prefix + 'total_score', 0)
    game_result_id = request.session.get(session_prefix + 'game_result_id')

    # If no game result exists in the session, create a new one
    if not game_result_id:
        game_result = GameResult.objects.create(user=request.user, scenario=scenario, score=0, total_questions=0)
        request.session[session_prefix + 'game_result_id'] = game_result.id
    else:
        try:
            game_result = GameResult.objects.get(id=game_result_id)
        except GameResult.DoesNotExist:
            return redirect('error')

    # Initialize the game if no questions have been selected yet
    if not selected_question_ids:
        initial_questions = scenario.questions.filter(difficulty='easy')
        if initial_questions.exists():
            first_question = random.choice(initial_questions)
            selected_question_ids = [first_question.id]
            request.session[session_prefix + 'selected_questions'] = selected_question_ids
        else:
            return render(request, 'game/error.html', {'message': 'No questions available for this scenario.'})

    # Check if the game is complete
    if question_index >= len(selected_question_ids):
        if len(selected_question_ids) >= 10:
            game_result.score = total_score
            game_result.total_questions = len(selected_question_ids)
            game_result.save()
            return redirect('game_complete', scenario_id=scenario_id)

        return redirect('scenario_question', scenario_id=scenario_id, question_index=0)

    # Get the current question
    current_question_id = selected_question_ids[question_index]
    current_question = get_object_or_404(scenario.questions, id=current_question_id)

    # Shuffle and store options in session to ensure randomness
    if f"{session_prefix}question_{current_question.id}_options_order" not in request.session:
        options = list(current_question.option_set.all())
        random.shuffle(options)
        request.session[f"{session_prefix}question_{current_question.id}_options_order"] = [option.id for option in options]
    else:
        option_ids = request.session[f"{session_prefix}question_{current_question.id}_options_order"]
        options = [get_object_or_404(current_question.option_set, id=opt_id) for opt_id in option_ids]

    explanation = None
    selected_option_id = request.session.get(session_prefix + 'selected_option_id', None)

    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action')  # Determine which button was clicked
        selected_option_id = request.POST.get('option')
        request.session[session_prefix + 'selected_option_id'] = selected_option_id  # Save selected option ID in session

        selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)

        if action == 'submit':
            # Show explanation regardless of whether the option is correct or incorrect
            if selected_option:
                explanation = selected_option.explanation
                # Add points regardless of whether the option is correct or incorrect
                total_score += selected_option.points
                request.session[session_prefix + 'total_score'] = total_score

            # Render the current page again with the explanation and "Next" button
            return render(request, 'game/scenario_question.html', {
                'scenario': scenario,
                'current_question': current_question,
                'options': options,
                'explanation': explanation,
                'selected_option_id': selected_option_id,
                'current_question_number': question_index + 1,
                'total_questions': 10,
                'show_next': True  # Indicate that the "Next" button should be displayed
            })

        elif action == 'next':
            # Move to the next question
            if len(selected_question_ids) < 10:
                next_question = decide_next_question(
                    request.user,
                    current_question,
                    selected_option_id,
                    selected_question_ids
                )

                # Ensure next question is unique
                while next_question and next_question.id in selected_question_ids:
                    next_question = decide_next_question(
                        request.user,
                        current_question,
                        selected_option_id,
                        selected_question_ids
                    )

                if next_question:
                    selected_question_ids.append(next_question.id)
                    request.session[session_prefix + 'selected_questions'] = selected_question_ids

            return redirect('scenario_question', scenario_id=scenario_id, question_index=question_index + 1)

    # Initial rendering of the page before the user selects an option
    return render(request, 'game/scenario_question.html', {
        'scenario': scenario,
        'current_question': current_question,
        'options': options,
        'explanation': explanation,
        'selected_option_id': selected_option_id,
        'current_question_number': question_index + 1,
        'total_questions': 10,
        'show_next': False  # No "Next" button until the user clicks "Submit"
    })

