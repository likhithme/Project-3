from django.contrib import admin
from .models import CustomUser, Scenario, Question, Option

class OptionInline(admin.TabularInline):
    model = Option
    fk_name = 'question'  # Specify the ForeignKey to 'Question' here

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]

from django.contrib import admin
from .models import GameResult

@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'scenario', 'score', 'total_questions', 'completed_at')
    list_filter = ('scenario', 'completed_at')
    search_fields = ('user__username', 'scenario__title')
    ordering = ('-completed_at',)
    actions = ['delete_selected']

def delete_selected(self, request, queryset):
    queryset.delete()
    self.message_user(request, "Selected results have been deleted.")
delete_selected.short_description = "Delete selected results"



admin.site.register(CustomUser)
admin.site.register(Scenario)
admin.site.register(Question, QuestionAdmin)
