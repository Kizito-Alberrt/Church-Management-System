from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
import datetime 
# from django_countries.fields import CountryField

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', _('Admin')),
        ('MAIN_REVEREND', _('Main Reverend')),
        ('PASTOR', _('Pastor')),
    )
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PASTOR')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name=_('Created By')
    )
    
    # Fix for the reverse accessor clash
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="church_user_set",
        related_query_name="church_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="church_user_set",
        related_query_name="church_user",
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')
    main_reverend = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    limit_choices_to={'role': 'MAIN_REVEREND'})
    
    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['province', 'name']
        unique_together = ('name', 'province')
    
    def __str__(self):
        return f"{self.name}, {self.province.name}"

class Church(models.Model):
    name = models.CharField(max_length=200)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='churches')
    pastor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                             limit_choices_to={'role': 'PASTOR'}, related_name = 'churches')
    address = models.TextField()
    established_date = models.DateField()
    
    class Meta:
        verbose_name = _('Church')
        verbose_name_plural = _('Churches')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.district})"

class Worshiper(models.Model):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    )
    first_name = models.CharField(max_length=100, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'))
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='worshipers', verbose_name=_('Church'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone Number'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    is_baptized = models.BooleanField(default=False, verbose_name=_('Is Baptized'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name=_('Gender'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Date of Birth'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def get_age(self):
        if self.date_of_birth:
            today = datetime.date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    class Meta:
        verbose_name = _('Worshiper')
        verbose_name_plural = _('Worshipers')
        indexes = [
            models.Index(fields=['is_baptized']),
            models.Index(fields=['gender']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['email']),
            models.Index(fields=['church']),
        ]

class NextOfKin(models.Model):
    RELATIONSHIP_CHOICES = (
        ('SPOUSE', _('Spouse')),
        ('PARENT', _('Parent')),
        ('CHILD', _('Child')),
        ('SIBLING', _('Sibling')),
        ('OTHER', _('Other')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='next_of_kin')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    class Meta:
        verbose_name = _('Next of Kin')
        verbose_name_plural = _('Next of Kin')
    
    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"

class MedicalHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=200)
    diagnosis_date = models.DateField()
    treatment = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Medical History')
        verbose_name_plural = _('Medical Histories')
        ordering = ['-diagnosis_date']
    
    def __str__(self):
        return f"{self.user}: {self.condition}"

class AttendanceRecord(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    male_count = models.PositiveIntegerField(default=0)
    female_count = models.PositiveIntegerField(default=0)
    children_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')
        ordering = ['-date']
        unique_together = ('church', 'date')
    
    def __str__(self):
        return f"{self.church} - {self.date}"
    
    def total_attendance(self):
        return self.male_count + self.female_count + self.children_count

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    emails_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    target_audience = models.CharField(max_length=20, choices=(
        ('ALL', _('All Users')),
        ('REVERENDS', _('Main Reverends and Pastors')),
        ('PASTORS', _('Pastors Only')),
    ), default='ALL')
    
    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title



class Attendance(models.Model):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    total = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = _('attendance')
        verbose_name_plural = _('attendances')
        unique_together = ('church', 'date')
    
    def __str__(self):
        return f"{self.church.name} - {self.date} - {self.total}"