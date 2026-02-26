from django.shortcuts import render


def index(request):
    """Index page view for ElephantChat"""
    return render(request, "index.html")
