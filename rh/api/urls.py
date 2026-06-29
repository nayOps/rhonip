from django.urls import path
from .views import *
from .views.guichet import (
    GuichetEmployeeList,
    GuichetEmployeeLookup,
    GuichetEmployeeRefs,
    GuichetEmployeeUpsert,
    GuichetGeography,
)
from .views.attendance_device import (
    AttendanceDeviceAPI,
    TabletEmployeeDataAPI,
    TabletEmployeeDayStatusAPI,
    TabletFingerprintBinaryAPI,
    TabletFingerprintEnrollAPI,
    TabletFingerprintEnrollStatusAPI,
    TabletFingerprintMatchingAPI,
    TabletFingerprintBundleAPI,
)

app_name = 'api'

urlpatterns = [
    path('guichet/refs/', GuichetEmployeeRefs.as_view(), name='guichet-refs'),
    path('guichet/geography/', GuichetGeography.as_view(), name='guichet-geography'),
    path('guichet/employees/', GuichetEmployeeList.as_view(), name='guichet-employees'),
    path('guichet/employee/lookup/', GuichetEmployeeLookup.as_view(), name='guichet-employee-lookup'),
    path('guichet/employee/upsert/', GuichetEmployeeUpsert.as_view(), name='guichet-employee-upsert'),
    path('attendance', AttendanceDeviceAPI.as_view(), name='attendance-device'),
    path('data', TabletEmployeeDataAPI.as_view(), name='tablet-data'),
    path('fingerprints/matching', TabletFingerprintMatchingAPI.as_view(), name='tablet-fingerprints-matching'),
    path('fingerprints/bundle', TabletFingerprintBundleAPI.as_view(), name='tablet-fingerprints-bundle'),
    path('fingerprints/enroll', TabletFingerprintEnrollAPI.as_view(), name='tablet-fingerprint-enroll'),
    path('fingerprints/enroll/status/<int:employee_id>', TabletFingerprintEnrollStatusAPI.as_view(), name='tablet-fingerprint-enroll-status'),
    path('fingerprints/<int:employee_id>/<str:finger_name>', TabletFingerprintBinaryAPI.as_view(), name='tablet-fingerprint-binary'),
    path('attendance/day-status/<int:employee_id>', TabletEmployeeDayStatusAPI.as_view(), name='tablet-day-status'),
    path('list/<str:app>/<str:model>', List.as_view(), name='list'),
    path('create/<str:app>/<str:model>', Create.as_view(), name='create'),
    path('detail/<str:app>/<str:model>/<int:pk>', Detail.as_view(), name='detail'),
    path('autocomplete/<str:app>/<str:model>/<str:to_field>', Autocomplete.as_view(), name='autocomplete')
]
