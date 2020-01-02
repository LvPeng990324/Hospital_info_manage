from django.contrib import admin
from .models import Sicker, Doctor, Department, Medicine, MedicineCategory, Prescription, ReceptionAdmin, MedicineAdmin


@admin.register(Sicker)
class SickerInformation(admin.ModelAdmin):
    list_display = ('sicker_id', 'name', 'gender', 'phone', 'home_location', 'department', 'doctor_id', 'money_to_pay')


@admin.register(Doctor)
class DoctorInformation(admin.ModelAdmin):
    list_display = ('doctor_id', 'name', 'gender', 'phone', 'department', 'sicker_num')


@admin.register(Department)
class DepartmentInformation(admin.ModelAdmin):
    list_display = ('name', 'department_id', 'master_id')


@admin.register(MedicineCategory)
class MedicineCategoryInformation(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Medicine)
class MedicineInformation(admin.ModelAdmin):
    list_display = ('name', 'introduction', 'category', 'price', 'remain_number')


@admin.register(Prescription)
class PrescriptionInformation(admin.ModelAdmin):
    list_display = ('prescription_id', 'doctor_id', 'sicker_id', 'given_date')


@admin.register(ReceptionAdmin)
class ReceptionAdminInformation(admin.ModelAdmin):
    list_display = ('reception_admin_id', 'password', 'name', 'gender', 'phone')


@admin.register(MedicineAdmin)
class MedicineAdminInformation(admin.ModelAdmin):
    list_display = ('medicine_admin_id', 'password', 'name', 'gender', 'phone')

