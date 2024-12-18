from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import RoleUpdateForm, ContestForm, StageForm, CriterionForm, SubmissionForm, EvaluationForm, AwardForm
from .models import Contest, Stage, Submission, Evaluation, Criterion, ContestParticipant
from django.contrib.auth.decorators import user_passes_test

CustomUser = get_user_model()


# Функция проверки, является ли пользователь администратором
def is_admin(user):
    return user.role == 'admin'


# Список конкурсов
@user_passes_test(is_admin)
def contest_list(request):
    contests = Contest.objects.all()
    return render(request, 'admin/contest_list.html', {'contests': contests})


def generate_report(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    submissions = Submission.objects.filter(contest=contest)

    report = []
    for submission in submissions:
        evaluations = Evaluation.objects.filter(submission=submission)
        total_points = sum([evaluation.points for evaluation in evaluations])
        report.append({
            'submission': submission,
            'total_points': total_points,
        })

    return render(request, 'admin/report.html', {'contest': contest, 'report': report})


def home_view(request):
    contests = Contest.objects.all()
    return render(request, 'main/pages/home.html', {'contests': contests})


def manage_users_view(request):
    query = request.GET.get('q')
    users = CustomUser.objects.all()

    # Если есть запрос, делаем фильтрацию
    if query:
        query_parts = query.split()
        filter_condition = Q()
        for part in query_parts:
            part = part.capitalize()  # Преобразование первой буквы в заглавную
            filter_condition |= Q(first_name__icontains=part) | Q(last_name__icontains=part) | Q(
                middle_name__icontains=part) | Q(email__icontains=part)
        users = users.filter(filter_condition)

    if request.method == 'POST':
        form = RoleUpdateForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            role = form.cleaned_data['role']
            user = CustomUser.objects.get(id=user_id)
            user.role = role  # Обновляем роль
            user.save()  # Сохраняем изменения
            return redirect('manage_users')  # Обновляем страницу

    else:
        form = RoleUpdateForm()

    context = {
        'users': users,
        'form': form,
    }
    return render(request, 'main/pages/manage_users.html', context)


def create_contest(request):
    if request.method == 'POST':
        form = ContestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ContestForm()
    return render(request, 'admin/contest_create.html', {'form': form})


def edit_contest(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    if request.method == 'POST':
        form = ContestForm(request.POST, instance=contest)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ContestForm(instance=contest)
    return render(request, 'admin/contest_edit.html', {'form': form})


def create_stage(request, contest_id):
    contest = Contest.objects.get(id=contest_id)

    if request.method == 'POST':
        form = StageForm(request.POST)
        if form.is_valid():
            # Вставляем contest в данные формы, чтобы автоматически использовать его
            stage = form.save(commit=False)
            stage.contest = contest
            stage.save()
            return redirect('contest_detail', contest.id)
    else:
        form = StageForm(initial={'contest': contest})  # Устанавливаем contest как начальное значение

    return render(request, 'moderator/add_stage.html', {'form': form, 'contest': contest})


def contest_detail(request, id):
    contest = get_object_or_404(Contest, id=id)
    return render(request, 'user/contest_detail.html', {'contest': contest})


def stage_edit(request, id):
    stage = get_object_or_404(Stage, id=id)

    if request.method == 'POST':
        form = StageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            return redirect('contest_detail', id=stage.contest.id)  # Перенаправление на страницу конкурса
    else:
        form = StageForm(instance=stage)

    return render(request, 'moderator/stage_edit.html', {'form': form, 'stage': stage})


def delete_stage(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)

    if request.method == 'POST':
        # Удаляем этап
        stage.delete()
        messages.success(request, "Этап был успешно удален.")
        return redirect('contest_detail', id=stage.contest.id)  # Используем 'id' вместо 'contest_id'

    return redirect('contest_detail', id=stage.contest.id)  # Используем 'id' вместо 'contest_id'


def stage_detail(request, id):
    # Получаем этап по его ID
    stage = get_object_or_404(Stage, id=id)

    # Получаем все критерии для этого этапа
    criteria = Criterion.objects.filter(stage=stage)

    # Если форма отправляется (например, для создания критерия)
    if request.method == 'POST':
        form = CriterionForm(request.POST)
        if form.is_valid():
            criterion = form.save(commit=False)
            criterion.stage = stage  # Устанавливаем этап в критерий перед сохранением
            criterion.save()
            return redirect('stage_detail', id=stage.id)
    else:
        # Если GET-запрос, создаем форму с текущим этапом в initial
        form = CriterionForm(initial={'stage': stage})  # Передаем текущий этап в форму

    # Отправляем в контекст информацию о стадии, критериях и форме
    return render(request, 'moderator/stage_detail.html', {
        'stage': stage,
        'criteria': criteria,
        'form': form
    })


# под вопросом
def create_criterion(request, stage_id):
    # Получаем этап по его ID
    stage = get_object_or_404(Stage, id=stage_id)

    if request.method == 'POST':
        # Если форма отправлена, создаем форму с данными из POST
        form = CriterionForm(request.POST)
        if form.is_valid():
            # Устанавливаем этап в форму перед сохранением
            criterion = form.save(commit=False)
            criterion.stage = stage  # Устанавливаем этап перед сохранением
            criterion.save()
            # Перенаправляем на страницу этапа после сохранения
            return redirect('stage_detail', id=stage.id)
    else:
        # Если это GET-запрос, создаем форму с текущим этапом в initial
        form = CriterionForm(initial={'stage': stage})

    return render(request, 'moderator/criterion_form.html', {'form': form, 'stage': stage})


def delete_criterion(request, criterion_id):
    # Получаем критерий по ID
    criterion = get_object_or_404(Criterion, id=criterion_id)

    # Проверка, что пользователь имеет право удалять критерий (опционально)
    # Например, если нужно, можно добавить проверку на роль пользователя
    if request.method == 'POST':
        criterion.delete()  # Удаляем критерий
        return redirect('stage_detail', id=criterion.stage.id)  # Перенаправляем обратно на страницу этапа


def submit_work(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    contest = stage.contest  # Получаем конкурс, связанный с этапом

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.stage = stage
            submission.contest = contest
            submission.save()

            # Добавляем пользователя в участников конкурса, если он еще не добавлен
            ContestParticipant.objects.get_or_create(
                user=request.user,
                contest=contest
            )

            return redirect('home')
    else:
        form = SubmissionForm()

    return render(request, 'user/submit_work.html', {'form': form, 'stage': stage})


def evaluate_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    # Получаем все критерии, связанные с текущим этапом конкурса
    criteria = Criterion.objects.filter(stage=submission.stage)

    if request.method == 'POST':
        for criterion in criteria:
            points = request.POST.get(f'points_{criterion.id}')
            if points:
                # Создаем или обновляем оценку для данного критерия
                evaluation, created = Evaluation.objects.update_or_create(
                    expert=request.user,  # Эксперт - текущий пользователь
                    submission=submission,
                    criterion=criterion,
                    defaults={'points': int(points)},
                )
        return redirect('submission_detail', submission_id=submission.id)

    return render(request, 'expert/evaluate_submission.html', {
        'submission': submission,
        'criteria': criteria,
    })


def expert_contests(request):
    # Получаем конкурсы, связанные с этапами, где пользователь является экспертом
    contests = Contest.objects.filter(stages__experts=request.user).distinct()
    return render(request, 'expert/contests.html', {'contests': contests})


def expert_stages(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    # Фильтруем этапы, где пользователь является экспертом
    stages = contest.stages.filter(experts=request.user)
    return render(request, 'expert/stages.html', {'contest': contest, 'stages': stages})


def expert_submissions(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    # Получаем работы, которые пользователь еще не оценил
    submissions = Submission.objects.filter(stage=stage).exclude(evaluation__expert=request.user)

    return render(request, 'expert/submissions.html', {'stage': stage, 'submissions': submissions})


def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'expert/contests.html', {'submission': submission})


def submission_detail_and_evaluate(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    # Получаем все критерии, связанные с текущим этапом конкурса
    criteria = Criterion.objects.filter(stage=submission.stage)

    if request.method == 'POST':
        # Обработка оценок
        for criterion in criteria:
            points = request.POST.get(f'points_{criterion.id}')
            if points:
                # Создаем или обновляем оценку для данного критерия
                evaluation, created = Evaluation.objects.update_or_create(
                    expert=request.user,  # Эксперт - текущий пользователь
                    submission=submission,
                    criterion=criterion,
                    defaults={'points': int(points)},
                )
        return redirect('expert_contests')

    return render(request, 'expert/submission_detail_and_evaluate.html', {
        'submission': submission,
        'criteria': criteria,
    })


def award_create_view(request, contest_id=None):
    contest = get_object_or_404(Contest, pk=contest_id)

    # Получаем участников, которые зарегистрированы в данном конкурсе
    participants = ContestParticipant.objects.filter(contest=contest)

    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AwardForm()
        form.fields['participant'].queryset = participants  # Ограничиваем список участников
        form.fields['contest'].initial = contest  # Предзаполняем поле конкурса

    return render(request, 'moderator/award_form.html', {'form': form})


