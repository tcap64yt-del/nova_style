from django.shortcuts import render
from user.models import Users


def admin_login(request):
    return render(request,'staff/admin_login.html')


def admin_user_managment(request):
    users=Users.objects.all()
    total=Users.objects.count()
    return render(request,'staff/admin_user_management.html',{"users":users,"total":total})