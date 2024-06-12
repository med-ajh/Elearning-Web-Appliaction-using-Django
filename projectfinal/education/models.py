from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.dispatch import receiver

class Profile(models.Model):
    LEVEL_CHOICES = [
        (1, "1ère année cycle ingénieur"),
        (2, "2ème année cycle ingénieur"),
        (3, "3ème année cycle ingénieur"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    enrolled_courses = models.ManyToManyField('Course', blank=True, related_name='enrolled_students')
    level = models.IntegerField(choices=LEVEL_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        is_admin = instance.is_superuser
        Profile.objects.create(user=instance, is_admin=is_admin)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))

class Course(models.Model):
    LEVEL_CHOICES = (
        (1, 'Cycle ingénieur 1'),
        (2, 'Cycle ingénieur 2'),
        (3, 'Cycle ingénieur 3'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    level = models.IntegerField(choices=LEVEL_CHOICES)
    file = models.FileField(upload_to='courses/', null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    grade = models.FloatField(null=True, blank=True)  # Permettre les valeurs nulles et vides
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class PerformanceAnalysis(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'is_teacher': False})
    analysis_date = models.DateTimeField(auto_now_add=True)
    recommendations = models.TextField()

    def __str__(self):
        return f'Analysis for {self.student.user.username} on {self.analysis_date}'
class Resource(models.Model):
    SUBJECT_CHOICES = [
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
        ('TutoredProject2', 'Projet tutoré 2'),
        ('Cryptography', 'Cryptographie'),
        ('LinuxAdmin', 'Sécurité et administration Système Linux'),
        ('NetworkSecurity', 'Sécurité des réseaux et Cloud'),
        ('AppSec', 'Sécurité applicative au développent des SI'),
        ('ERP', 'ERP : ODOO et SAP'),
        ('LaborIP', 'Droit de travail et propriété intellectuelle'),
        ('ProjectManagement', 'Management de projets et agilité'),
        ('LangCom5', 'Langues et communication 5'),
    ]

    RESOURCE_TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Vidéo'),
        ('exercise', 'Exercice'),
        ('file', 'Fichier')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES)
    level = models.IntegerField(choices=[
        (2, "2ème année cycle ingénieur"),
        (3, "3ème année cycle ingénieur"),
    ])
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title