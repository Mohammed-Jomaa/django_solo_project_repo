from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse
import json
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request,'index.html')

def register(request):
    return render(request,'register.html')

def login(request):
    return render(request,'login.html')


def create_user(request):
    if request.method == 'POST':
        errors = User.objects.user_validator(request.POST)
        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        hashed_pw = bcrypt.hashpw(
            request.POST['registerPassword'].encode(),
            bcrypt.gensalt()
        ).decode()

        user = User.objects.create(
            first_name=request.POST['registerFirstName'],
            last_name=request.POST['registerLastName'],
            email=request.POST['registerEmail'],
            birth_day=request.POST['registerBirthDay'],
            password=hashed_pw,
            role='parent'
        )

        request.session['name'] = f"{user.first_name} {user.last_name}"
        return JsonResponse({'success': True, 'message': 'تم إنشاء الحساب بنجاح!'})

    return JsonResponse({'success': False, 'errors': {'general': 'طلب غير صالح'}})

def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)

        errors = User.objects.login_validator(data)
        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        user = User.objects.filter(email=data['loginEmail']).first()
        request.session['name'] = f"{user.first_name} {user.last_name}"
        request.session['user_id'] = user.id

        return JsonResponse({'success': True, 'redirect_url': '/dashboard'})

    return JsonResponse({'success': False, 'errors': {'general': 'طلب غير صالح'}})

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    families = FamilyMember.objects.filter(user=user)
    
    context = {
        'families' : families,
    }
    return render(request,'dashboard.html',context)

def logout(request):
    request.session.flush()
    return redirect('/')

def new_family(request):
    if 'user_id' not in request.session:
        return redirect('index')
    return render(request,'new_family.html')

def create_family(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            return redirect('index')
        errors = Family.objects.validate_family(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return render(request,'new_family.html')


        family = Family.objects.create(
            name=request.POST['familyName'],
            owner=User.objects.get(id=request.session['user_id'])
        )
        family_member = FamilyMember.objects.create(
            family = family,
            user = User.objects.get(id=request.session['user_id'])
        )

        return redirect('dashboard')

    return redirect('dashboard')


def manage_family(request,id):
    if 'user_id' not in request.session:
            return redirect('index')
    context ={
        'family' : Family.objects.get(id=id)
    }
    return render(request,'manage_family.html',context)


def add_admin(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            return redirect('index')

        family_id = request.POST['family_id']
        errors = User.objects.validate_admin_email(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect(reverse('manage_family', args=[family_id]))

        email = request.POST['email']
        user = User.objects.filter(email=email).first()
        family = Family.objects.get(id=family_id)

        if FamilyMember.objects.filter(family=family, user=user).exists():
            messages.warning(request, 'هذا المستخدم عضو بالفعل في العائلة')
        else:
            FamilyMember.objects.create(family=family, user=user)
            messages.success(request, 'تمت إضافة المشرف بنجاح')

        return redirect(reverse('manage_family', args=[family_id]))

    return redirect('dashboard')

def delete_family(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            return JsonResponse({'success': False, 'error': 'يجب تسجيل الدخول'})

        family_id = request.POST.get('family_id')
        try:
            family = Family.objects.get(id=family_id)
            if family.owner.id != request.session['user_id']:
                return JsonResponse({'success': False, 'error': 'فقط صاحب العائلة يمكنه الحذف'})
            family.delete()
            return JsonResponse({'success': True, 'redirect_url': '/dashboard'})
        except Family.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'العائلة غير موجودة'})

    return JsonResponse({'success': False, 'error': 'طلب غير صالح'})

def task_list(request, id):
    return render(request, 'tasks/task_list.html')

def review_tasks(request, id):
    return render(request, 'tasks/review_tasks.html')

def children(request, id):
    return render(request, 'tasks/children.html')

def rewards(request, id):
    return render(request, 'tasks/rewards.html')

    