from django import forms

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from pydantic import ValidationError

from .models import Contest, Stage, Criterion, Submission, Evaluation, Award

from django.utils import timezone

CustomUser = get_user_model()


class RoleUpdateForm(forms.Form):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['title', 'start_date', 'end_date', 'description', 'status', 'moderators']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'moderators': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'description': 'Описание',
            'status': 'Статус',
            'moderators': 'Модераторы',
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['contest', 'title', 'start_date', 'end_date', 'experts']

    # Настройка поля 'contest' с использованием HiddenInput
    contest = forms.ModelChoiceField(
        queryset=Contest.objects.all(),
        required=True,
        label="Конкурс",
        widget=forms.HiddenInput()  # Скрываем поле для пользователя
    )

    start_date = forms.DateField(
        widget=forms.SelectDateWidget(),
        required=True,
        label="Дата начала"
    )
    end_date = forms.DateField(
        widget=forms.SelectDateWidget(),
        required=True,
        label="Дата окончания"
    )

    experts = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='user'),  # Фильтрация по роли пользователя
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Эксперты"
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Дата начала не может быть позже даты окончания.")

        return cleaned_data


class CriterionForm(forms.ModelForm):
    class Meta:
        model = Criterion
        fields = ['stage', 'name', 'max_points']  # Указываем, какие поля будут в форме

    # Убедитесь, что поле "stage" не выводится для пользователя
    stage = forms.ModelChoiceField(queryset=Stage.objects.all(), required=True, widget=forms.HiddenInput())


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'file']  # Параметры, которые видит пользователь

    # Временное отключение проверки
    # def clean(self):
    #     cleaned_data = super().clean()
    #     stage = cleaned_data.get("stage")
    #     if stage and timezone.now().date() > stage.end_date:
    #         raise ValidationError("Работа должна быть подана до конца текущего этапа.")
    #     return cleaned_data


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['points']

    def __init__(self, *args, **kwargs):
        submission = kwargs.get('submission')
        super().__init__(*args, **kwargs)

        # Получаем все критерии для данной работы
        self.fields['points'].queryset = Criterion.objects.filter(submission=submission)


class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = ['participant', 'contest', 'place', 'award_description']
        labels = {
            'participant': 'Участник',
            'contest': 'Конкурс',
            'place': 'Место',
            'award_description': 'Описание награды',
        }
        widgets = {
            'award_description': forms.Textarea(attrs={
                'placeholder': 'Введите описание награды...',
                'rows': 4,
            }),
        }