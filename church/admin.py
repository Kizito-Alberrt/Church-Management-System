from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *



# In church/admin.py
@admin.action(description='Assign to default district')
def assign_to_default_district(modeladmin, request, queryset):
    default_district, created = District.objects.get_or_create(
        name='Default District',
        defaults={'province': Province.objects.first()}
    )
    queryset.update(district=default_district)

class UserAdmin(admin.ModelAdmin):
    actions = [assign_to_default_district]

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                                       'profile_picture', 'date_of_birth', 'address')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'main_reverend')
    list_filter = ('province',)
    search_fields = ('name', 'province__name')
    raw_id_fields = ('main_reverend',)
    list_editable = ('main_reverend',)
    autocomplete_fields = ['main_reverend']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'ADMIN':
            return qs
        elif request.user.role == 'MAIN_REVEREND':
            return qs.filter(main_reverend=request.user)
        return qs.none()

class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'pastor', 'established_date')
    list_filter = ('district__province', 'district')
    search_fields = ('name', 'district__name', 'pastor__first_name', 'pastor__last_name')
    raw_id_fields = ('pastor',)
    list_editable = ('pastor',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'ADMIN':
            return qs
        elif request.user.role == 'MAIN_REVEREND':
            return qs.filter(district__main_reverend=request.user)
        return qs.none()


class WorshiperAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'church', 'is_baptized', 'get_baptized', 'get_gender', 'get_age')
    list_filter = ('is_baptized', 'gender', 'church__district', 'church__district__province')
    search_fields = ('first_name', 'last_name', 'email')
    list_select_related = ('church', 'church__district', 'church__district__province')
    list_editable = ('is_baptized',)
    actions = ['mark_baptized', 'mark_not_baptized']
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'church')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'email')
        }),
        (_('Personal Details'), {
            'fields': ('is_baptized', 'gender', 'date_of_birth')
        }),
    )
    actions = ['mark_baptized', 'mark_not_baptized']

    @admin.display(description=_('Is Baptized'))
    def get_baptized(self, obj):
        return obj.is_baptized

    @admin.display(description=_('Gender'))
    def get_gender(self, obj):
        return obj.get_gender_display() or _('Unknown')

    @admin.display(description=_('Age'))
    def get_age(self, obj):
        age = obj.get_age()
        return age if age is not None else _('Unknown')

    @admin.action(description=_('Mark selected worshipers as baptized'))
    def mark_baptized(self, request, queryset):
        queryset.update(is_baptized=True)

    @admin.action(description=_('Mark selected worshipers as not baptized'))
    def mark_not_baptized(self, request, queryset):
        queryset.update(is_baptized=False)

class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'relationship', 'phone_number')
    list_filter = ('relationship',)
    search_fields = ('name', 'user__first_name', 'user__last_name')

class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'condition', 'diagnosis_date')
    list_filter = ('diagnosis_date',)
    search_fields = ('user__first_name', 'user__last_name', 'condition')
    date_hierarchy = 'diagnosis_date'

class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('church', 'date', 'total_attendance', 'recorded_by')
    list_filter = ('church__district', 'date')
    search_fields = ('church__name', 'recorded_by__first_name', 'recorded_by__last_name')
    date_hierarchy = 'date'

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published', 'target_audience')
    list_filter = ('is_published', 'target_audience', 'created_at')
    search_fields = ('title', 'content', 'author__first_name', 'author__last_name')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Church, ChurchAdmin)
admin.site.register(Worshiper, WorshiperAdmin)
admin.site.register(NextOfKin, NextOfKinAdmin)
admin.site.register(MedicalHistory, MedicalHistoryAdmin)
admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(News, NewsAdmin)