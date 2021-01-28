from django.views.generic import TemplateView


class RegisterStartPageView(TemplateView):
    template_name = "register/start.html"