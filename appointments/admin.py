from django.contrib import admin
from .models import Doctor, Appointment, Department, MedicalRecord, Prescription

admin.site.site_header = "Administration"
admin.site.site_title = "Administration"
admin.site.index_title = ""

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'department', 'available_days']
    list_filter = ['department', 'specialization']
    search_fields = ['name', 'specialization']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['token_number', 'patient_name', 'patient_email', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_editable = ['status']  # This enables the dropdown in the list view
    list_display_links = ['token_number', 'patient_name']  # These will be clickable to open the detail view
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient_name', 'patient_email', 'doctor__name', 'token_number']
    readonly_fields = ['token_number', 'created_at']

    class Media:
        js = ('appointments/js/admin_status_confirm.js',)
    
    fieldsets = (
        ('Token & Status', {
            'fields': ('token_number', 'status', 'created_at')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_email', 'patient_phone')
        }),
        ('Appointment Details', {
            'fields': ('doctor', 'appointment_date', 'appointment_time', 'reason')
        }),
    )

class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient_email', 'doctor', 'visit_date', 'diagnosis']
    list_filter = ['doctor', 'visit_date']
    search_fields = ['patient_email', 'diagnosis']
    inlines = [PrescriptionInline]

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medical_record', 'medication_name', 'dosage', 'frequency']
    search_fields = ['medication_name', 'medical_record__patient_email']