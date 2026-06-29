from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View

from django.shortcuts import render

from django.http import Http404

from django.urls import reverse_lazy



from employee.utils.profile_dossier import build_profile_dossier





class MyProfile(LoginRequiredMixin, View):

    template_name = "employee/my_profile.html"



    def get(self, request):

        if not hasattr(request.user, 'employee') or not request.user.employee:

            raise Http404("Aucun profil d'employé associé à votre compte")



        employee = request.user.employee

        can_edit = request.user.has_perm('employee.change_employee')



        from employee.models import Education, Document, Experience



        educations = Education.objects.filter(employee=employee).order_by('-diploma_year', '-end_date')

        documents = Document.objects.filter(employee=employee).order_by('-pk')

        experiences = Experience.objects.filter(employee=employee).order_by('-start_date')



        edit_url = reverse_lazy('employee:change', kwargs={'pk': employee.id}) if can_edit else None



        return render(request, self.template_name, {

            'employee': employee,

            'dossier': build_profile_dossier(employee),

            'educations': educations,

            'documents': documents,

            'experiences': experiences,

            'can_edit': can_edit,

            'edit_url': edit_url,

            'full_dossier_url': edit_url,

        })


