from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse,HttpResponse
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
    if user.role != 'parent':
        return redirect('index')
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
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    return render(request,'new_family.html')

def create_family(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            return redirect('index')
        user = User.objects.get(id=request.session['user_id'])
        if user.role != 'parent':
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
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    context ={
        'family' : Family.objects.get(id=id)
    }
    return render(request,'manage_family.html',context)


def add_admin(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            return redirect('index')
        user = User.objects.get(id=request.session['user_id'])
        if user.role != 'parent':
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
        user = User.objects.get(id=request.session['user_id'])
        if user.role != 'parent':
            return redirect('index')

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
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)
    tasks = Task.objects.filter(family=family)
    context = {
        'family' : family,
        'tasks' : tasks,
    }
    return render(request, 'tasks/task_list.html',context)

def review_tasks(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    return render(request, 'tasks/review_tasks.html')

def children(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    return render(request, 'children/children.html')


def rewards(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)
    rewards = Reward.objects.filter(family=family)

    context = {
        'family': family,
        'rewards': rewards,
    }
    return render(request, 'rewards/rewards.html', context)

def add_task(request, id):
    if 'user_id' not in request.session:
        return JsonResponse({'success': False, 'errors': {'general': 'غير مسموح'}})
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)

    if request.method == 'POST':
        data = json.loads(request.body)
        errors = Task.objects.validate_task(data)
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        Task.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            due_date=data.get('due_date') or None,
            family=family,
            created_by=User.objects.get(id=request.session['user_id'])
        )
        return JsonResponse({'success': True, 'message': 'تمت إضافة المهمة بنجاح!'})
    
    return render(request, 'tasks/add_task.html', {'family': family})


def delete_task(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=id)
            family_id = task.family.id
            task.delete()
            return redirect('task_list', id=family_id)
        except Task.DoesNotExist:
            messages.error(request, "المهمة غير موجودة")
            return redirect('dashboard')

    return redirect('dashboard')

def children(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)
    children_members = FamilyMember.objects.filter(family=family, user__role='child')

    children_with_points = []
    for member in children_members:
        child = member.user
        total_points = PointsTransaction.objects.filter(child=child).aggregate(total=models.Sum('points'))['total'] or 0
        children_with_points.append({
            'child': child,
            'points': total_points
        })

    context = {
        'family': family,
        'children_with_points': children_with_points
    }
    return render(request, 'children/children.html', context)

def create_child(request,id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)
    return render(request,'children/add_child.html',{'family': family})



def add_child(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        errors = User.objects.child_validator(data)
        user = User.objects.get(id=request.session['user_id'])
        if user.role != 'parent':
            return redirect('index')
        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        hashed_pw = bcrypt.hashpw(
            data['password'].encode(),
            bcrypt.gensalt()
        ).decode()

        user = User.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            birth_day=data['birth_day'],
            password=hashed_pw,
            role='child'
        )

        family = Family.objects.get(id=id)
        FamilyMember.objects.create(user=user, family=family)

        return JsonResponse({'success': True, 'message': 'تم إضافة الطفل بنجاح!'})

    return JsonResponse({'success': False, 'errors': {'general': 'طلب غير صالح'}})


def create_reward(request,id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    family = Family.objects.get(id=id)
    return render(request,'rewards/create_reward.html',{'family' : family })


def add_reward(request, id):
    if 'user_id' not in request.session:
        return JsonResponse({'success': False, 'errors': {'general': 'غير مصرح'}})
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')

        errors = Reward.objects.validate_rewards(data)
        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        Reward.objects.create(
            title=data['name'],
            points_cost=data['points'],
            image=image,
            family=Family.objects.get(id=id),
            created_by=User.objects.get(id=request.session['user_id'])
        )

        return JsonResponse({'success': True, 'message': 'تمت إضافة الجائزة بنجاح!'})
    
    return JsonResponse({'success': False, 'errors': {'general': 'طلب غير صالح'}})

def delete_reward(request, id):
    if 'user_id' not in request.session:
        return redirect('index')
    user = User.objects.get(id=request.session['user_id'])
    if user.role != 'parent':
        return redirect('index')
    if request.method == 'POST':
        try:
            reward = Reward.objects.get(id=id)
            family_id = reward.family.id
            reward.delete()
            return redirect('rewards', id=family_id)
        except Task.DoesNotExist:
            messages.error(request, "الجائزة غير موجودة")
            return redirect('dashboard')

    return redirect('dashboard')