from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models

class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)


class Scenario(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=10, choices=[('kids', 'Kids'), ('teens', 'Teens'), ('adults', 'Adults')])

    def __str__(self):
        return self.title


class Question(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('difficult', 'Difficult')],
        default='easy'
    )

    def __str__(self):
        return self.text



class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # ForeignKey to Question
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)    
    explanation = models.TextField(blank=True, null=True)  # New field

    def __str__(self):
        return self.text


class GameResult(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="game_results")
    scenario = models.ForeignKey('Scenario', on_delete=models.CASCADE, related_name="results")
    score = models.IntegerField()
    total_questions = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.scenario.title} - {self.score}/{self.total_questions}"
