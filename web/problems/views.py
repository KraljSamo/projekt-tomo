from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import Form, IntegerField
from django.http import HttpResponse
from problems.models import Problem, Part
from courses.models import ProblemSet, Course
from users.models import User
from attempts.models import Attempt, HistoricalAttempt
from utils.views import plain_text
from utils import verify


@login_required
def problem_attempt_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_view_problem(problem))
    filename, contents = problem.attempt_file(user=request.user)
    return plain_text(filename, contents, content_type=problem.content_type())


@login_required
def problem_edit_file(request, problem_pk):
    """Download an attempt file for a given problem."""
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_edit_problem(problem))
    filename, contents = problem.edit_file(user=request.user)
    return plain_text(filename, contents, content_type=problem.content_type())


@login_required
def problem_move(request, problem_pk, shift):
    problem = get_object_or_404(Problem, pk=problem_pk)
    verify(request.user.can_edit_problem_set(problem.problem_set))
    problem.move(shift)
    return redirect(problem)


class ProblemCreate(CreateView):
    '''
    Create new problem by specifying title and description.
    '''
    model = Problem
    fields = ['title', 'description', 'language']

    def get_context_data(self, **kwargs):
        context = super(ProblemCreate, self).get_context_data(**kwargs)
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        verify(self.request.user.can_edit_problem_set(problem_set))
        context['problem_set'] = problem_set
        return context

    def form_valid(self, form):
        problem_set = get_object_or_404(ProblemSet, id=self.kwargs['problem_set_id'])
        verify(self.request.user.can_edit_problem_set(problem_set))
        form.instance.author = self.request.user
        form.instance.problem_set = problem_set
        return super(ProblemCreate, self).form_valid(form)


class ProblemUpdate(UpdateView):
    '''
    Update problem title and description.
    '''
    model = Problem
    fields = '__all__'

    def get_object(self, *args, **kwargs):
        obj = super(ProblemUpdate, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_problem(obj))
        return obj

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ProblemUpdate, self).form_valid(form)

    def get_success_url(self):
        return self.object.problem_set.get_absolute_url()


class ProblemDelete(DeleteView):
    '''
    Delete a problem and all it's parts and attempts.
    '''
    model = Problem

    def get_success_url(self):
        return self.object.problem_set.get_absolute_url()

    def get_object(self, *args, **kwargs):
        obj = super(ProblemDelete, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_problem(obj))
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProblemDelete, self).get_context_data(**kwargs)
        return context


class CopyProblemForm(Form):
    problem_set_id = IntegerField(label='Problem set id')


def copy_form(request, problem_pk):
    """
    Show and react to CopyForm.
    """
    problem = Problem.objects.get(pk=problem_pk)
    verify(request.user.can_view_problem(problem))
    if request.method == 'POST':
        form = CopyProblemForm(request.POST)
        if form.is_valid():
            problem_set_pk = form.cleaned_data['problem_set_id']
            problem_set = ProblemSet.objects.get(pk=problem_set_pk)
            verify(request.user.can_edit_problem_set(problem_set))
            problem.copy_to(problem_set)
            return redirect(problem_set)
        else:
            # TODO: handle errors
            response = HttpResponse("Please select a problem set.")
            return response
    else:
        form = CopyProblemForm()
        courses = request.user.taught_courses.all()
        return render(
            request, 'courses/problem_copy_form.html',
            {
                'form': form,
                'courses': courses,
                'problem': problem
            }
        )


@login_required
def problem_solution(request, problem_pk, user_pk):
    """Show problem solution."""
    problem = Problem.objects.get(pk=problem_pk)
    student = get_object_or_404(User, pk=user_pk)
    verify(request.user.can_view_problem_solution(problem, student))
    problem_set = problem.problem_set
    attempts = student.attempts.filter(part__problem__id=problem_pk)
    parts = problem.parts.all()

    for part in parts:
        try:
            part.attempt = attempts.get(part=part)
        except:
            part.attempt = None
    return render(request, 'problems/solutions.html',
                  {
                      'problem': problem,
                      'problem_set': problem_set,
                      'parts': parts,
                      'student': student,
                      'is_teacher': request.user.can_edit_problem_set(problem_set),
                  }
                  )

@login_required
def all_solutions_to_part(request, part_pk):
    part = get_object_or_404(Part, pk=part_pk)
    problem = part.problem
    problem_set = problem.problem_set
    course = problem_set.course
    students = course.observed_students()
    attempts = Attempt.objects.filter(part__id=part_pk).filter(user__id__in=students).order_by('-user')

    for st, podnaloga in enumerate(problem.parts.all()):
        if podnaloga.id == part.id:
            stevilka_podnaloge = st + 1

    return render(request, 'problems/all_solutions.html',
                  {
                      'part': part,
                      'problem' : problem,
                      'problem_set' : problem_set,
                      'attempts' : attempts,
                      'part_number' : stevilka_podnaloge,
                    }
                  )

@login_required
def problem_solution_at_time(request, problem_pk, user_pk, hist_attempt_pk):
    hist_attempt = get_object_or_404(HistoricalAttempt, pk=hist_attempt_pk)
    problem = get_object_or_404(Problem, pk = problem_pk)
    problem_set = problem.problem_set
    parts = problem.parts.all()
    veljavne_oddaje = HistoricalAttempt.objects.filter(user__id=user_pk).filter(
        submission_date__lte=hist_attempt.submission_date).filter(
            part__id__in=parts)
    podnaloge = dict()
    for st, part in enumerate(parts):
        viable = veljavne_oddaje.filter(part__id = part.id)
        if viable:
            podnaloge[st] = viable.latest('submission_date')
        else:
            podnaloge[st] = False
    return render(request, 'problems/solution_at_time.html',
                  {
                      'time' : hist_attempt.submission_date,
                      'data' : podnaloge,
                      'problem' : problem,
                      'problem_set' : problem_set,
                      'is_teacher': request.user.can_edit_problem_set(problem_set),
                      })














