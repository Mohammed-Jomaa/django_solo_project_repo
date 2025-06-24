from django.db import models
import re
import bcrypt
from datetime import date

# ====== MANAGER ======
class UserManager(models.Manager):
    def user_validator(self, postdata):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        if len(postdata['registerFirstName']) < 2:
            errors['registerFirstName'] = "الاسم الأول يجب أن لا يقل عن حرفين"
        elif not postdata['registerFirstName'].isalpha():
            errors['registerFirstName'] = "الاسم الأول يجب أن يحتوي على أحرف فقط"

        if len(postdata['registerLastName']) < 2:
            errors['registerLastName'] = "الاسم الأخير يجب أن لا يقل عن حرفين"
        elif not postdata['registerLastName'].isalpha():
            errors['registerLastName'] = "الاسم الأخير يجب أن يحتوي على أحرف فقط"

        if not EMAIL_REGEX.match(postdata['registerEmail']):
            errors['registerEmail'] = "بريد إلكتروني غير صالح"

        if User.objects.filter(email=postdata['registerEmail']).exists():
            errors['registerEmail'] = "هذا البريد الإلكتروني مسجل مسبقًا"

        if len(postdata['registerPassword']) < 8:
            errors['registerPassword'] = "كلمة المرور يجب أن لا تقل عن 8 أحرف"

        if postdata['registerRepeatPassword'] != postdata['registerPassword']:
            errors['registerRepeatPassword'] = "كلمتا المرور غير متطابقتين"

        birth_day = postdata.get('registerBirthDay')
        if birth_day:
            try:
                birth_date = date.fromisoformat(birth_day)
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                if age < 18:
                    errors['registerBirthDay'] = "يجب أن يكون عمرك 18 سنة على الأقل"
            except ValueError:
                errors['registerBirthDay'] = "صيغة تاريخ الميلاد غير صحيحة"
        else:
            errors['registerBirthDay'] = "يرجى إدخال تاريخ الميلاد"

        return errors

    def login_validator(self, postdata):
        errors = {}
        email = postdata.get('loginEmail')
        password = postdata.get('loginPassword')
        if not email or not password:
            errors['login'] = "البريد الإلكتروني وكلمة المرور مطلوبة"
            return errors

        user = User.objects.filter(email=email).first()
        if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
            errors['login'] = "البريد الإلكتروني أو كلمة المرور غير صحيحة"
            return errors
        return errors
    
    def validate_admin_email(self, postdata):
        errors = {}
        email = postdata.get('email')
        if not email:
            errors['email'] = "البريد الإلكتروني مطلوب"
            return errors
        user = User.objects.filter(email=email).first()
        if not user:
            errors['email'] = "البريد الإلكتروني غير صحيح"
        return errors


            

class FamilyManager(models.Manager):
    def validate_family(self,postdata):
        errors = {}
        if len(postdata['familyName']) < 2:
            errors['familyName'] = "اسم العائلة يجب أن لا يقل عن حرفين"
        return errors

# ====== MODELS ======

class User(models.Model):
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('child', 'Child'),
    )
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(unique=True)
    birth_day = models.DateField()
    password = models.CharField(max_length=60)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='child')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class Family(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_families')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = FamilyManager()


class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    child = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'child'})
    proof = models.ImageField(upload_to='task_proofs/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)


class Reward(models.Model):
    title = models.CharField(max_length=100)
    points_cost = models.PositiveIntegerField()
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PointsTransaction(models.Model):
    child = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'child'})
    points = models.IntegerField()  
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ClaimedReward(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    )

    child = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'child'})
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.first_name} طلب {self.reward.title} - {self.status}"
