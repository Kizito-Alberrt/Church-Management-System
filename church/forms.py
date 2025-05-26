from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import User, Worshiper, NextOfKin, MedicalHistory, AttendanceRecord, News, Province, District, Church

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                 'profile_picture', 'date_of_birth', 'address')

class WorshiperForm(forms.ModelForm):
    class Meta:
        model = Worshiper
        fields = ['first_name', 'last_name', 'church', 'phone_number', 'email', 'is_baptized', 'gender', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'church': _('Church'),
            'phone_number': _('Phone Number'),
            'email': _('Email'),
            'is_baptized': _('Is Baptized'),
            'gender': _('Gender'),
            'date_of_birth': _('Date of Birth'),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            if user.role == 'PASTOR':
                # Pastors can only select their own church
                church = Church.objects.filter(pastor=user).first()
                if church:
                    self.fields['church'].queryset = Church.objects.filter(id=church.id)
                    self.fields['church'].initial = church
                    self.fields['church'].widget.attrs['readonly'] = True  # Optional: Make field read-only
                else:
                    self.fields['church'].queryset = Church.objects.none()  # No churches available
            elif user.role == 'MAIN_REVEREND':
                # Main Reverends can select churches in their district
                district = District.objects.filter(main_reverend=user).first()
                if district:
                    self.fields['church'].queryset = Church.objects.filter(district=district)
                else:
                    self.fields['church'].queryset = Church.objects.none()

class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        fields = '__all__'

class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        widgets = {
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'PASTOR':
            self.fields['church'].queryset = Church.objects.filter(pastor=user)
            self.fields['recorded_by'].initial = user
            self.fields['recorded_by'].widget = forms.HiddenInput()
        elif user and user.role == 'MAIN_REVEREND':
            self.fields['church'].queryset = Church.objects.filter(district__main_reverend=user)

class NewsForm(forms.ModelForm):
    send_notification = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Send email notification to users'),
        help_text=_('Uncheck if you don\'t want to send emails about this news')
    )
    class Meta:
        model = News
        fields = ['title', 'content', 'target_audience', 'is_published', 'send_notification']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and self.user.role == 'MAIN_REVEREND':
            self.fields['target_audience'].choices = [
                ('ALL', 'All Users'),
                ('REVERENDS', 'Main Reverends and Pastors'),
                ('PASTORS', 'Pastors Only'),
            ]
        elif self.user and self.user.role == 'PASTOR':
            self.fields['target_audience'].choices = [
                ('ALL', 'All Users'),
            ]
            self.fields['target_audience'].initial = 'ALL'
            self.fields['target_audience'].widget.attrs['disabled'] = True
    def save(self, commit=True):
        news = super().save(commit=False)
        news.author = self.user
        if commit:
            news.save()
        return news
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )



class ProvinceForm(forms.ModelForm):
    class Meta:
        model = Province
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DistrictForm(forms.ModelForm):
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    main_reverend = forms.ModelChoiceField(
        queryset=User.objects.filter(role='MAIN_REVEREND'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = District
        fields = ['name', 'province', 'main_reverend']

class ChurchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and self.user.role == 'MAIN_REVEREND':
            district = District.objects.get(main_reverend=self.user)
            self.fields['district'].queryset = District.objects.filter(pk=district.pk)
            self.fields['district'].initial = district
            self.fields['pastor'].queryset = User.objects.filter(role='PASTOR', churches__district=district)
        elif self.user and (self.user.is_superuser or self.user.role == 'ADMIN'):
            self.fields['district'].queryset = District.objects.all()
            self.fields['pastor'].queryset = User.objects.filter(role='PASTOR')

    class Meta:
        model = Church
        fields = ['name', 'district', 'pastor', 'address', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


# forms.py - Add these new forms

class MainReverendCreationForm(UserCreationForm):
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),  # Will be populated via JS
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'province', 'district')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = District.objects.filter(province_id=province_id)
            except (ValueError, TypeError):
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'MAIN_REVEREND'
        if commit:
            user.save()
            district = self.cleaned_data['district']
            district.main_reverend = user
            district.save()
        return user

class PastorCreationForm(UserCreationForm):
    church = forms.ModelChoiceField(
        queryset=Church.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'church')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            if self.user.role == 'MAIN_REVEREND':
                district = District.objects.get(main_reverend=self.user)
                self.fields['church'].queryset = Church.objects.filter(district=district)
            elif self.user.is_superuser or self.user.role == 'ADMIN':
                self.fields['church'].queryset = Church.objects.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PASTOR'
        if commit:
            user.save()
            church = self.cleaned_data['church']
            church.pastor = user
            church.save()
        return user


class AdminUserSearchForm(forms.Form):
    province = forms.ModelChoiceField(queryset=Province.objects.all(), required=False, label=_('Province'))
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False, label=_('District'))
    church = forms.ModelChoiceField(queryset=Church.objects.all(), required=False, label=_('Church'))
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by first or last name')}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.select_related('province')
        self.fields['church'].queryset = Church.objects.select_related('district__province')

class AdminChurchSearchForm(forms.Form):
    province = forms.ModelChoiceField(queryset=Province.objects.all(), required=False, label=_('Province'))
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False, label=_('District'))
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by church name')}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.select_related('province')

class AdminWorshiperSearchForm(forms.Form):
    gender = forms.ChoiceField(choices=[('', _('All'))] + list(Worshiper.GENDER_CHOICES), required=False, label=_('Gender'))
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by first or last name')}))

class ReverendChurchSearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by church name')}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == 'MAIN_REVEREND':
            district = District.objects.filter(main_reverend=user).first()
            self.district = district if district else None

class ReverendPastorSearchForm(forms.Form):
    church = forms.ModelChoiceField(queryset=Church.objects.all(), required=False, label=_('Church'))
    gender = forms.ChoiceField(choices=[('', _('All')), ('M', _('Male')), ('F', _('Female')), ('O', _('Other'))], required=False, label=_('Gender'))
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by first or last name')}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == 'MAIN_REVEREND':
            district = District.objects.filter(main_reverend=user).first()
            if district:
                self.fields['church'].queryset = Church.objects.filter(district=district).select_related('district__province')
            else:
                self.fields['church'].queryset = Church.objects.none()

class PastorWorshiperSearchForm(forms.Form):
    gender = forms.ChoiceField(choices=[('', _('All'))] + list(Worshiper.GENDER_CHOICES), required=False, label=_('Gender'))
    name = forms.CharField(max_length=100, required=False, label=_('Name'), widget=forms.TextInput(attrs={'placeholder': _('Search by first or last name')}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == 'PASTOR':
            church = Church.objects.filter(pastor=user).first()
            self.church = church if church else None



class PastorAssignChurchForm(forms.Form):
    pastor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='PASTOR'),
        label=_('Pastor'),
        empty_label=_('Select Pastor'),
        required=True
    )
    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        label=_('Church'),
        empty_label=_('Select Church'),
        required=True
    )

    
    def clean(self):
        cleaned_data = super().clean()
        pastor = cleaned_data.get('pastor')
        church = cleaned_data.get('church')
        if pastor and pastor.role != 'PASTOR':
            raise forms.ValidationError(_('Selected user is not a pastor.'))
        if church and church.pastor and church.pastor != pastor:
            raise forms.ValidationError(_('This church is already assigned to another pastor.'))
        if pastor and pastor.churches.exists():
            raise forms.ValidationError(_('This pastor is already assigned to a church. A pastor can only be assigned to one church.'))
        return cleaned_data



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'phone_number', 'role', 'pastor_category')
        labels = {
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'gender': _('Gender'),
            'phone_number': _('Phone Number'),
            'role': _('Role'),
            'pastor_category': _('Pastor Category'),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match.'))
        return password2

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        pastor_category = cleaned_data.get('pastor_category')
        if role == 'PASTOR' and not pastor_category:
            raise forms.ValidationError(_('Pastor category is required for pastors.'))
        if role != 'PASTOR' and pastor_category:
            raise forms.ValidationError(_('Pastor category can only be set for pastors.'))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'phone_number', 'role', 'pastor_category')
        labels = {
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'gender': _('Gender'),
            'phone_number': _('Phone Number'),
            'role': _('Role'),
            'pastor_category': _('Pastor Category'),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        pastor_category = cleaned_data.get('pastor_category')
        if role == 'PASTOR' and not pastor_category:
            raise forms.ValidationError(_('Pastor category is required for pastors.'))
        if role != 'PASTOR' and pastor_category:
            raise forms.ValidationError(_('Pastor category can only be set for pastors.'))
        return cleaned_data