from django.shortcuts import render,redirect
from user.models import Users
from django.contrib import messages
from django.contrib.auth import login ,logout,authenticate
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def admin_login(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        admin=authenticate(email=email,password=password)

        if admin:
            if admin.is_staff and admin.is_superuser:
                login(request,admin)
                return redirect("user_management")
        else:
            messages.error(request,"invaild credentials")

    if request.is_authenticated:
        if not request.user.is_staff:
            return redirect('home')
        return redirect('user_management')

    return render(request,'staff/admin_login.html')

@login_required(login_url='admin_login')
def user_managment(request):
    users=Users.objects.all()
    total=Users.objects.count()
    sort = request.GET.get('sort', 'all')
    search = request.GET.get('search', '')

    if sort=='newest':
        users=users.order_by('-created_at')
    elif sort == 'oldest':
        users = users.order_by('created_at')

    if search:
        users=users.filter(Q(name__icontains=search) |Q(email__icontains=search))

    return render(request,'staff/admin_user_management.html',{"users":users,"total":total,"sort":sort,"search":search})


def block_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    if user:
        user.status = False
        user.save(update_fields=["status"])
    
    return redirect('user_management')

def unblock_user(request, user_id):
    user = Users.objects.filter(id=user_id).first()
    user.status = True
    user.save()
    return redirect("user_management")