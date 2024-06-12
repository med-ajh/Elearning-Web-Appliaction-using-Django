from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import SignUpForm, UserProfileUpdateForm, CourseForm, AssignmentForm, SubmissionForm, GradeForm, ResourceForm
from .models import Course, Assignment, Submission, Grade, Profile, PerformanceAnalysis, Resource
import logging
import os
import json
from django.conf import settings
import pandas as pd
import matplotlib.pyplot as plt

def is_teacher(user):
    return user.profile.is_teacher

def is_admin_or_teacher(user):
    return user.is_superuser or user.profile.is_teacher

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(data=request.POST, user=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
        return redirect('profile')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'password_form': password_form
    })

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User {user.username} logged in successfully.")
                if user.is_superuser:
                    logger.info(f"Redirecting superuser {user.username} to admin dashboard.")
                    return redirect('admin_dashboard')
                elif user.profile.is_teacher:
                    logger.info(f"Redirecting teacher {user.username} to teacher dashboard.")
                    return redirect('teacher_dashboard')
                else:
                    logger.info(f"Redirecting student {user.username} to student dashboard.")
                    return redirect('student_dashboard')
            else:
                logger.error(f"Authentication failed for user {username}.")
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            logger.error("Form validation failed.")
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'student/student_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'teacher/teacher_dashboard.html')

@login_required
def course_list(request):
    if request.user.is_superuser:
        courses = Course.objects.all()
        can_create = True
    elif request.user.profile.is_teacher:
        courses = Course.objects.filter(teacher=request.user)
        can_create = True
    else:
        courses = Course.objects.filter(level=request.user.profile.level)
        can_create = False
    return render(request, 'course_list.html', {'courses': courses, 'can_create': can_create})

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_admin_or_teacher)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            logger.info(f"Cours créé avec succès: {course.title}, fichier: {course.file}")
            messages.success(request, 'Cours créé avec succès.')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_teacher)
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cours mis à jour avec succès.')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_teacher)
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Cours supprimé avec succès.')
        return redirect('course_list')
    return render(request, 'course_confirm_delete.html', {'course': course})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})

@login_required
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('assignment_list')
    else:
        form = AssignmentForm(user=request.user)
    return render(request, 'assignment_form.html', {'form': form})


import logging

logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment).select_related('student')

    if request.method == 'POST':
        if not request.user.profile.is_teacher and not request.user.is_superuser:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.save()
                messages.success(request, 'Devoir soumis avec succès.')
                return redirect('assignment_detail', assignment_id=assignment.id)
        else:
            grade_form = GradeForm(request.POST)
            submission_id = request.POST.get('submission')
            logger.info(f"Received submission_id: {submission_id}")
            if grade_form.is_valid() and submission_id:
                grade_value = grade_form.cleaned_data['grade']
                comments_value = grade_form.cleaned_data['comments']
                logger.info(f"Received grade: {grade_value}, comments: {comments_value}")

                # Assurez-vous que la valeur de `grade` est présente
                if grade_value is not None:
                    submission = get_object_or_404(Submission, id=submission_id)
                    grade, created = Grade.objects.get_or_create(assignment=assignment, student=submission.student, submission=submission)
                    grade.grade = grade_value
                    grade.comments = comments_value
                    grade.save()
                    messages.success(request, 'Note et commentaire ajoutés avec succès.')
                    return redirect('assignment_detail', assignment_id=assignment.id)
                else:
                    messages.error(request, 'La note ne peut pas être vide.')
                    logger.error(f"Grade value is None. grade_form.errors: {grade_form.errors}")
            else:
                messages.error(request, 'Le formulaire est invalide ou l\'ID de soumission est manquant.')
                logger.error(f"Form is invalid or submission_id is missing: {grade_form.errors}")

    form = SubmissionForm()
    grade_form = GradeForm()

    # Create a list of submissions with grades
    enriched_submissions = []
    for submission in submissions:
        grade = Grade.objects.filter(assignment=assignment, student=submission.student).first()
        enriched_submissions.append({
            'submission': submission,
            'grade': grade.grade if grade else None,
            'comments': grade.comments if grade else None
        })

    return render(request, 'assignment_detail.html', {
        'assignment': assignment,
        'submissions': enriched_submissions,
        'form': form,
        'grade_form': grade_form
    })


    # Create a list of submissions with grades
    enriched_submissions = []
    for submission in submissions:
        grade = Grade.objects.filter(assignment=assignment, student=submission.student).first()
        enriched_submissions.append({
            'submission': submission,
            'grade': grade.grade if grade else None,
            'comments': grade.comments if grade else None
        })

    return render(request, 'assignment_detail.html', {
        'assignment': assignment,
        'submissions': enriched_submissions,
        'form': form,
        'grade_form': grade_form
    })

@login_required
@user_passes_test(is_admin_or_teacher)
def assignment_update(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Devoir mis à jour avec succès.')
            return redirect('assignment_list')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'assignment_form.html', {'form': form})

@login_required
def assignment_list(request):
    if request.user.is_superuser:
        assignments = Assignment.objects.all()
        can_create = True
    elif request.user.profile.is_teacher:
        assignments = Assignment.objects.filter(course__teacher=request.user)
        can_create = True
    else:
        assignments = Assignment.objects.filter(course__level=request.user.profile.level)
        can_create = False
    return render(request, 'assignment_list.html', {'assignments': assignments, 'can_create': can_create})

@login_required
@user_passes_test(is_admin_or_teacher)
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Devoir supprimé avec succès.')
        return redirect('assignment_list')
    return render(request, 'assignment_confirm_delete.html', {'assignment': assignment})

@login_required
@user_passes_test(is_admin_or_teacher)
def submission_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'submission_list.html', {'assignment': assignment, 'submissions': submissions})

@login_required
@user_passes_test(is_admin_or_teacher)
def submission_update(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Soumission mise à jour avec succès.')
            return redirect('assignment_detail', assignment_id=submission.assignment.id)
    else:
        form = SubmissionForm(instance=submission)
    return render(request, 'submission_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_teacher)
def submission_delete(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Soumission supprimée avec succès.')
        return redirect('assignment_detail', assignment_id=submission.assignment.id)
    return render(request, 'submission_confirm_delete.html', {'submission': submission})

@login_required
@user_passes_test(is_teacher)
def grade_submission(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.assignment = assignment
            grade.save()
            messages.success(request, 'Note enregistrée avec succès.')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = GradeForm()
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'grade_submission.html', {'assignment': assignment, 'submissions': submissions, 'form': form})

import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting
import matplotlib.pyplot as plt
from .models import Profile, Grade

@login_required
def view_performance(request):
    user = request.user
    grades = Grade.objects.filter(student=user).select_related('assignment')
    
    # Get the teacher profile
    teacher = Profile.objects.filter(level=user.profile.level, is_teacher=True).first()
    teacher_grades = Grade.objects.filter(student=teacher.user).select_related('assignment') if teacher else []

    if not grades and not teacher_grades:
        messages.info(request, "Aucune performance enregistrée.")
        return render(request, 'view_performance.html', {'grades': grades, 'teacher_grades': teacher_grades})

    # Convert to DataFrame
    data = pd.DataFrame.from_records(grades.values('assignment__title', 'grade'))
    teacher_data = pd.DataFrame.from_records(teacher_grades.values('assignment__title', 'grade'))

    # Create performance graph for student
    if not data.empty:
        plt.figure(figsize=(6, 4))  # Adjust the figure size here
        plt.plot(data['assignment__title'], data['grade'], marker='o')
        plt.title('Student Performance Graph')
        plt.xlabel('Assignments')
        plt.ylabel('Grades')
        plt.xticks(rotation=45)
        plt.tight_layout()
        student_graph_path = os.path.join(settings.BASE_DIR, 'education', 'static', 'graphs', f'performance_{user.id}.png')
        plt.savefig(student_graph_path)
        plt.close()
    else:
        student_graph_path = None

    # Create performance graph for teacher
    if not teacher_data.empty:
        plt.figure(figsize=(6, 4))  # Adjust the figure size here
        plt.plot(teacher_data['assignment__title'], teacher_data['grade'], marker='o')
        plt.title('Teacher Performance Graph')
        plt.xlabel('Assignments')
        plt.ylabel('Grades')
        plt.xticks(rotation=45)
        plt.tight_layout()
        teacher_graph_path = os.path.join(settings.BASE_DIR, 'education', 'static', 'graphs', f'teacher_performance_{teacher.user.id}.png')
        plt.savefig(teacher_graph_path)
        plt.close()
    else:
        teacher_graph_path = None

    # Generate improvement advice
    improvement_advice = "Basé sur vos résultats actuels, il est recommandé de revoir les concepts clés et de pratiquer davantage les exercices. N'hésitez pas à demander de l'aide si nécessaire."

    return render(request, 'view_performance.html', {
        'grades': grades,
        'graph_path': f'graphs/performance_{user.id}.png' if student_graph_path else None,
        'teacher_graph_path': f'graphs/teacher_performance_{teacher.user.id}.png' if teacher_graph_path else None,
        'improvement_advice': improvement_advice,
        'teacher_grades': teacher_grades,
        'teacher': teacher
    })

@login_required
@user_passes_test(lambda u: u.profile.is_teacher)
def performance_analysis(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Profile, id=student_id)
        grades = Grade.objects.filter(student=student.user).select_related('assignment')
        
        if not grades:
            messages.info(request, "Aucune performance enregistrée pour cet étudiant.")
            return render(request, 'performance_analysis.html', {'students': Profile.objects.filter(is_teacher=False, level=request.user.profile.level)})

        # Convert to DataFrame
        data = pd.DataFrame.from_records(grades.values('assignment__title', 'grade'))

        if data.empty:
            messages.info(request, "Aucune performance à afficher pour cet étudiant.")
            return render(request, 'performance_analysis.html', {'students': Profile.objects.filter(is_teacher=False, level=request.user.profile.level)})

        # Create performance graph with smaller size
        plt.figure(figsize=(6, 4))  # Adjust the figure size here
        plt.plot(data['assignment__title'], data['grade'], marker='o')
        plt.title('Performance Graph')
        plt.xlabel('Assignments')
        plt.ylabel('Grades')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save graph to the existing 'education/static/graphs' directory
        graph_path = os.path.join(settings.BASE_DIR, 'education', 'static', 'graphs', f'performance_{student_id}.png')
        try:
            plt.savefig(graph_path)
            plt.close()
            messages.info(request, f"Graph saved at {graph_path}")
        except Exception as e:
            messages.error(request, f"Error saving graph: {e}")
            return render(request, 'performance_analysis.html', {'students': Profile.objects.filter(is_teacher=False, level=request.user.profile.level)})

        # Generate improvement advice based on average grade
        average_grade = data['grade'].mean()

        if average_grade < 5:
            improvement_advice = (
                "Vos performances sont très faibles. Il est crucial de revoir les bases des sujets abordés. "
                "Assurez-vous de comprendre les concepts fondamentaux et n'hésitez pas à demander de l'aide immédiatement. "
                "Il est fortement recommandé de participer activement en classe et de pratiquer régulièrement."
            )
        elif 5 <= average_grade < 10:
            improvement_advice = (
                "Vos performances sont en dessous de la moyenne. Il est important de consacrer plus de temps à l'étude et à la pratique. "
                "Rejoignez des sessions d'étude supplémentaires et essayez de clarifier vos doutes avec votre professeur ou vos camarades."
            )
        elif 10 <= average_grade < 15:
            improvement_advice = (
                "Vos performances sont moyennes. Continuez à travailler régulièrement et essayez de renforcer les domaines où vous rencontrez des difficultés. "
                "Utilisez des ressources supplémentaires pour approfondir vos connaissances."
            )
        elif 15 <= average_grade < 20:
            improvement_advice = (
                "Vos performances sont bonnes. Continuez ainsi et essayez d'atteindre l'excellence en vous challengeant avec des problèmes plus complexes. "
                "Participez à des activités et des projets supplémentaires pour améliorer vos compétences."
            )
        else:
            improvement_advice = (
                "Excellent travail! Vous avez des performances exceptionnelles. Continuez à maintenir ce niveau de qualité et "
                "considérez de partager vos connaissances avec vos camarades ou de participer à des compétitions académiques."
            )

        analysis = PerformanceAnalysis.objects.create(student=student, recommendations=improvement_advice)
        return render(request, 'performance_analysis.html', {
            'student': student,
            'grades': grades,
            'graph_path': f'graphs/performance_{student_id}.png',
            'analysis': analysis,
            'students': Profile.objects.filter(is_teacher=False, level=request.user.profile.level)
        })

    students = Profile.objects.filter(is_teacher=False, level=request.user.profile.level)
    return render(request, 'performance_analysis.html', {'students': students})



@login_required
def resource_list(request):
    user = request.user
    if user.is_superuser:
        resources = Resource.objects.all()
    elif user.profile.is_teacher:
        resources = Resource.objects.filter(level=user.profile.level, created_by=user)
    else:
        resources = Resource.objects.filter(level=user.profile.level)
    return render(request, 'resource_list.html', {'resources': resources})

@login_required
@user_passes_test(lambda u: u.profile.is_teacher or u.is_superuser)
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.save()
            messages.success(request, 'Ressource pédagogique ajoutée avec succès.')
            return redirect('resource_list')
    else:
        form = ResourceForm(user=request.user)
    return render(request, 'resource_form.html', {'form': form})

@login_required
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    return render(request, 'resource_detail.html', {'resource': resource})

@login_required
@user_passes_test(lambda u: u.profile.is_teacher or u.is_superuser)
def resource_update(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ressource mise à jour avec succès.')
            return redirect('resource_detail', resource_id=resource.id)
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'resource_form.html', {'form': form, 'resource': resource})

@login_required
@user_passes_test(is_admin_or_teacher)
def resource_delete(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Ressource supprimée avec succès.')
        return redirect('resource_list')
    return render(request, 'resource_confirm_delete.html', {'resource': resource})

import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    user = request.user
    total_users = User.objects.count()
    total_students = Profile.objects.filter(is_teacher=False, is_admin=False).count()
    total_teachers = Profile.objects.filter(is_teacher=True).count()
    total_admins = User.objects.filter(is_superuser=True).count()
    total_courses = Course.objects.count()
    total_assignments = Assignment.objects.count()

    # Données pour les graphiques
    # Exemple de calcul des utilisateurs par mois
    user_chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    user_chart_data = [User.objects.filter(date_joined__month=i).count() for i in range(1, 7)]

    # Exemple de calcul des cours par niveau
    course_chart_labels = ['Level 1', 'Level 2', 'Level 3']
    course_chart_data = [
        Course.objects.filter(level=1).count(),
        Course.objects.filter(level=2).count(),
        Course.objects.filter(level=3).count(),
    ]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_admins': total_admins,
        'total_courses': total_courses,
        'total_assignments': total_assignments,
        'user_chart_labels': json.dumps(user_chart_labels),
        'user_chart_data': json.dumps(user_chart_data),
        'course_chart_labels': json.dumps(course_chart_labels),
        'course_chart_data': json.dumps(course_chart_data),
    }

    return render(request, 'dashboard.html', context)
@login_required
def admin_dashboard(request):
    return dashboard(request)

@login_required
def student_dashboard(request):
    return dashboard(request)

@login_required
def teacher_dashboard(request):
    return dashboard(request)