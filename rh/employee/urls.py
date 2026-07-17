from django.urls import path
from employee.views import *

app_name = 'employee'

urlpatterns = [
    path('attendance/schedule-settings/', AttendanceScheduleSettings.as_view(), name='attendance_schedule_settings'),
    path('payroll/', PayrollList.as_view(), name='payroll_list'),
    path('my-profile/', MyProfile.as_view(), name='my_profile'),
    path('my-attendance/', MyAttendance.as_view(), name='my_attendance'),
    path('attendance/overview/', CompanyAttendance.as_view(), name='company_attendance'),
    path('attendance/direction-reports/', DirectionReportHub.as_view(), name='direction_report_hub'),
    path('attendance/direction/<int:direction_id>/report/', DirectionAttendanceReport.as_view(), name='direction_attendance_report'),
    path('attendance/direction/<int:direction_id>/schedule/', DirectionReportSchedule.as_view(), name='direction_report_schedule'),
    path('statistics/', PresenceStatistics.as_view(), name='presence_statistics'),
    path('statistics/export.csv', PresenceStatisticsExport.as_view(), name='presence_statistics_export'),
    path('statistics/export.pdf', PresenceStatisticsPdfExport.as_view(), name='presence_statistics_pdf'),
    path('reports/generated/<str:filename>', GeneratedReportDownload.as_view(), name='generated_report_download'),
    path('reports/', ReportsHub.as_view(), name='reports_hub'),
    path('reports/biometric-enrollment/', BiometricEnrollmentReport.as_view(), name='biometric_enrollment_report'),
    path('reports/biometric-enrollment.pdf', BiometricEnrollmentReportExport.as_view(), name='biometric_enrollment_report_export'),
    path('reports/biometric-enrollment/schedule/', BiometricEnrollmentReportSchedule.as_view(), name='biometric_enrollment_report_schedule'),
    path('reports/enrollment-daily/', EnrollmentDayReport.as_view(), name='enrollment_day_report'),
    path('reports/enrollment-daily.pdf', EnrollmentDayReportExport.as_view(), name='enrollment_day_report_export'),
    path('reports/enrollment-daily/schedule/', EnrollmentDayReportSchedule.as_view(), name='enrollment_day_report_schedule'),
    path('reports/attendance-daily/', DailyAttendanceReport.as_view(), name='daily_attendance_report'),
    path('reports/attendance-daily.pdf', DailyAttendanceReportExport.as_view(), name='daily_attendance_report_export'),
    path('attendance/late-justification/new/', LateJustificationCreate.as_view(), name='late_justification_create'),
    path('export/agents-directory.pdf', AgentsDirectoryExport.as_view(), name='agents_directory_export'),
    path('change/<int:pk>', Employee.as_view(), name='change'),
    path('attendance/report/<int:pk>/', AttendanceReport.as_view(), name='attendance_report'),
    path('attendance/report/<int:pk>/schedule/', AttendanceReportSchedule.as_view(), name='attendance_report_schedule'),
    path('request_for_info/change/<int:pk>', RequestForInfo.as_view(), name='request_for_info_change'),
]
