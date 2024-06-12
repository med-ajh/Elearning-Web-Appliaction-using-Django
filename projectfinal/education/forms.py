from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile, Course, Assignment, Submission, Grade, Resource

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_teacher = forms.BooleanField(required=False, label="Inscription en tant qu'enseignant")
    level = forms.ChoiceField(choices=Profile.LEVEL_CHOICES, required=True, label="Niveau")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_teacher', 'level']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_teacher = self.cleaned_data['is_teacher']
            profile.level = self.cleaned_data['level']
            profile.save()
        return user

class UserProfileUpdateForm(UserChangeForm):
    password = None  # We do not want to show the password field

    class Meta:
        model = User
        fields = ['username', 'email']

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'start_date', 'end_date', 'level', 'file']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'course', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(level=user.profile.level)

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['grade', 'comments']
 
class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'link', 'file', 'subject', 'level', 'resource_type']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ResourceForm, self).__init__(*args, **kwargs)
        if user:
            if user.profile.level == 2:
                self.fields['subject'].choices = [
                    ('NetArch', 'Architecture .Net et communications'),
                    ('ClientServer', 'Client/serveur'),
                    ('MathIA', "Mathématiques pour l'intelligence artificielle"),
                    ('UML', 'Modélisation Objet avec UML'),
                    ('JavaJEE', 'Java avancée et Technologies JEE'),
                    ('DevOps1', 'DevOps 1'),
                    ('CostManagement', 'Management des coûts'),
                    ('LangCom3', 'Langues et communication 3'),
                    ('FullStackPython', 'Développement Full Stack Python'),
                    ('AngularIonic', 'Framework Angular et Ionic'),
                    ('DevOps2', 'DevOps 2'),
                    ('IA_BigData', "Fondements de l'IA et Big Data"),
                    ('OracleAdmin', 'Administration Oracle'),
                    ('LangCom4', 'Langues et communication 4'),
                    ('TutoredProject2', 'Projet tutoré 2')
                ]
            elif user.profile.level == 3:
                self.fields['subject'].choices = [
                    ('Cryptography', 'Cryptographie'),
                    ('LinuxAdmin', 'Sécurité et administration Système Linux'),
                    ('NetworkSecurity', 'Sécurité des réseaux et Cloud'),
                    ('AppSec', 'Sécurité applicative au développent des SI'),
                    ('ERP', 'ERP : ODOO et SAP'),
                    ('LaborIP', 'Droit de travail et propriété intellectuelle'),
                    ('ProjectManagement', 'Management de projets et agilité'),
                    ('LangCom5', 'Langues et communication 5')
                ]