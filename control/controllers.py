<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
"""
CONTROL LAYER — BCE Architecture
All business rules and orchestration live here.
No HTTP, no SQL — only pure logic delegating to/from Entity.


"""

import re
from werkzeug.security import generate_password_hash, check_password_hash
from entity.models import (
    UserEntity, CategoryEntity, FRAEntity, DonationEntity,
    FRAFavoriteEntity, CommentEntity, ReportEntity
)


# ── BaseController ────────────────────────────────────────────────────────────

class BaseController:
    """
    Shared helpers inherited by every controller.
    Keeps utility logic encapsulated inside the Control layer.
    """

    @classmethod
    def _safe(cls, user: dict) -> dict:
        """Strip password before returning user data to the Boundary layer."""
        return {k: v for k, v in user.items() if k != 'password'}

    @classmethod
    def _valid_email(cls, email: str) -> bool:
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))

    @classmethod
    def _verify_password(cls, stored_hash: str, provided: str) -> bool:
        """
        Single place for password verification.
        Handles both hashed passwords and the legacy plaintext fallback.
        """
        if stored_hash.startswith(('pbkdf2:', 'scrypt:')):
            return check_password_hash(stored_hash, provided)
        return stored_hash == provided  # legacy plaintext fallback


# ── AuthController ────────────────────────────────────────────────────────────

class AuthController(BaseController):

    @classmethod
    def login(cls, email: str, password: str):
        if not email or not password:
            return None, "Email and password are required"
        user = UserEntity.find_by_email(email.strip().lower())
        if not user:
            return None, "No account found with that email address"
        if not user['is_active']:
            return None, "This account has been deactivated. Please contact support."
        if not cls._verify_password(user['password'], password):
            return None, "Incorrect password"
        UserEntity.record_login(user['id'])
        return cls._safe(user), None

    @classmethod
    def register(cls, full_name: str, email: str, password: str,
                 confirm_password: str, role: str = 'donee'):
        full_name = (full_name or '').strip()
        email = (email or '').strip().lower()
        if len(full_name) < 2:
            return None, "Full name must be at least 2 characters"
        if not cls._valid_email(email):
            return None, "Please enter a valid email address"
        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters"
        if password != confirm_password:
            return None, "Passwords do not match"
        if role not in ('fundraiser', 'donee'):
            role = 'donee'
        # Control layer hashes the password before passing to Entity
        uid, err = UserEntity.create(full_name, email, generate_password_hash(password), role)
        if err:
            return None, err
        user = UserEntity.find_by_id(uid)
        return cls._safe(user), None


# ── ProfileController ─────────────────────────────────────────────────────────

class ProfileController(BaseController):

    @classmethod
    def get(cls, user_id: int):
        user = UserEntity.find_by_id(user_id)
        return cls._safe(user) if user else None

    @classmethod
    def update(cls, user_id: int, full_name: str, bio: str, phone: str, address: str):
        full_name = (full_name or '').strip()
        if len(full_name) < 2:
            return False, "Full name must be at least 2 characters"
        UserEntity.update(user_id, full_name=full_name, bio=bio or '',
                          phone=phone or '', address=address or '')
        return True, "Profile updated successfully"

    @classmethod
    def change_password(cls, user_id: int, current_password: str,
                        new_password: str, confirm_new: str):
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        if not cls._verify_password(user['password'], current_password):
            return False, "Current password is incorrect"
        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        if new_password != confirm_new:
            return False, "New passwords do not match"
        UserEntity.update_password(user_id, generate_password_hash(new_password))
        return True, "Password changed successfully"


# ── AdminController ───────────────────────────────────────────────────────────

class AdminController(BaseController):

    @classmethod
    def get_dashboard_data(cls, user_id: int) -> dict:
        return {'stats': cls.dashboard_stats()}

    @classmethod
    def get_dashboard_template(cls) -> str:
        return 'admin/dashboard.html'

    @classmethod
    def dashboard_stats(cls):
        users, total_users = UserEntity.search()
        role_counts = UserEntity.count_by_role()
        fra_stats = FRAEntity.platform_stats()
        return {
            'total_users': total_users,
            'active_users': sum(1 for u in users if u['is_active']),
            'role_counts': role_counts,
            'fra_stats': fra_stats,
            'total_raised': DonationEntity.platform_total(),
            'total_donations': DonationEntity.count_all(),
            'new_users_30d': UserEntity.count_new(30),
            'pending_fras': fra_stats.get('pending', 0),
        }

    # ── User management ──

    @classmethod
    def list_users(cls, search: str = '', role: str = None, is_active=None, page: int = 1):
        users, total = UserEntity.search(search, role or None, is_active, page)
        return [cls._safe(u) for u in users], total

    @classmethod
    def get_user(cls, user_id: int):
        user = UserEntity.find_by_id(user_id)
        if not user:
            return None, "User not found"
        return cls._safe(user), None

    @classmethod
    def create_user(cls, full_name: str, email: str, password: str, role: str):
        full_name = (full_name or '').strip()
        email = (email or '').strip().lower()
        if len(full_name) < 2:
            return None, "Full name must be at least 2 characters"
        if not cls._valid_email(email):
            return None, "Invalid email address"
        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters"
        if role not in ('admin', 'fundraiser', 'donee'):
            return None, "Invalid role"
        uid, err = UserEntity.create(full_name, email, generate_password_hash(password), role)
        return uid, err

    @classmethod
    def update_user(cls, user_id: int, full_name: str, email: str, role: str,
                    phone: str, address: str, bio: str):
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        updates = {}
        if full_name and len(full_name.strip()) >= 2:
            updates['full_name'] = full_name.strip()
        if email and cls._valid_email(email.strip().lower()):
            updates['email'] = email.strip().lower()
        if role and role in ('admin', 'fundraiser', 'donee'):
            updates['role'] = role
        if phone is not None:
            updates['phone'] = phone
        if address is not None:
            updates['address'] = address
        if bio is not None:
            updates['bio'] = bio
<<<<<<< HEAD
        ok, err = UserEntity.update(user_id, **updates)
        if not ok:
            return False, err
=======
        UserEntity.update(user_id, **updates)
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
        return True, "User updated successfully"

    @classmethod
    def deactivate_user(cls, user_id: int, requesting_id: int):
        if user_id == requesting_id:
            return False, "You cannot deactivate your own account"
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        if user['role'] == 'admin':
            return False, "Cannot deactivate another admin account"
        UserEntity.update(user_id, is_active=0)
        return True, f"{user['full_name']}'s account has been deactivated"

    @classmethod
    def reactivate_user(cls, user_id: int):
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        UserEntity.update(user_id, is_active=1)
        return True, f"{user['full_name']}'s account has been reactivated"

    @classmethod
    def delete_user(cls, user_id: int, requesting_id: int):
        if user_id == requesting_id:
            return False, "You cannot delete your own account"
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        if user['role'] == 'admin':
            return False, "Cannot delete an admin account"
        name = user['full_name']
        UserEntity.delete(user_id)
        return True, f"{name}'s account has been permanently deleted"

    @classmethod
    def reset_password(cls, user_id: int, new_password: str, requesting_id: int):
        if user_id == requesting_id:
            return False, "Use Change Password to update your own password"
        if not new_password or len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        user = UserEntity.find_by_id(user_id)
        if not user:
            return False, "User not found"
        UserEntity.update_password(user_id, generate_password_hash(new_password))
        return True, f"Password reset for {user['full_name']}"

    # ── Category management ──

    @classmethod
    def list_categories(cls, search: str = ''):
        return CategoryEntity.search(search)

    @classmethod
    def create_category(cls, name: str, description: str = ''):
        name = (name or '').strip()
        if len(name) < 2:
            return None, "Category name must be at least 2 characters"
        return CategoryEntity.create(name, description or '')

    @classmethod
    def update_category(cls, cat_id: int, name: str, description: str):
        cat = CategoryEntity.find_by_id(cat_id)
        if not cat:
            return False, "Category not found"
        name = (name or '').strip()
        if name and len(name) < 2:
            return False, "Category name must be at least 2 characters"
        ok, err = CategoryEntity.update(cat_id, name or None, description)
        if not ok:
            return False, err
        return True, "Category updated"

    @classmethod
    def delete_category(cls, cat_id: int):
        cat = CategoryEntity.find_by_id(cat_id)
        if not cat:
            return False, "Category not found"
        CategoryEntity.delete(cat_id)
        return True, f"Category '{cat['name']}' deleted"

    # ── FRA management ──

    @classmethod
    def list_fras(cls, search: str = '', status: str = None, category_id=None, page: int = 1):
        return FRAEntity.get_all(search, status, category_id, page)

    @classmethod
    def list_pending(cls):
        return FRAEntity.get_pending_approval()

    @classmethod
    def approve_fra(cls, fra_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return False, "FRA not found"
        if fra['status'] != 'pending_approval':
            return False, "FRA is not pending approval"
        FRAEntity.update_fields(fra_id, status='active')
        return True, f'"{fra["title"]}" has been approved and is now live'

    @classmethod
    def reject_fra(cls, fra_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return False, "FRA not found"
        if fra['status'] != 'pending_approval':
            return False, "FRA is not pending approval"
        FRAEntity.update_fields(fra_id, status='draft')
        return True, f'"{fra["title"]}" has been rejected and returned to draft'

    @classmethod
    def force_close_fra(cls, fra_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return False, "FRA not found"
        FRAEntity.update_fields(fra_id, status='closed')
        return True, f'"{fra["title"]}" has been closed'

    # ── Reports ──

    @classmethod
    def generate_report(cls, period: str = 'monthly'):
        breakdown = DonationEntity.period_breakdown(period)
        fra_stats = FRAEntity.platform_stats()
        days = {'daily': 30, 'weekly': 84, 'monthly': 365}.get(period, 365)
        return {
            'period': period,
            'breakdown': breakdown,
            'fra_stats': fra_stats,
            'total_raised': DonationEntity.platform_total(),
            'total_donations': DonationEntity.count_all(),
            'new_users': UserEntity.count_new(days),
        }

    @classmethod
    def list_reports(cls, keyword: str = None, status: str = None,
                     start_date: str = None, end_date: str = None):
        if status and status not in ('pending', 'reviewed'):
            status = None
        return ReportEntity.list_all(keyword or None, status, start_date or None, end_date or None)

    @classmethod
    def resolve_report(cls, report_id: int):
        ReportEntity.update_status(report_id, 'reviewed')
        return True, "Report marked as reviewed"


# ── FundraiserController ──────────────────────────────────────────────────────

class FundraiserController(BaseController):

    @classmethod
    def get_dashboard_data(cls, user_id: int) -> dict:
        return {
            'stats':  cls.get_stats(user_id),
            'recent': cls.list_my_fras(user_id)[:5],
        }

    @classmethod
    def get_dashboard_template(cls) -> str:
        return 'fundraiser/dashboard.html'

    @classmethod
    def get_stats(cls, user_id: int):
        return FRAEntity.owner_stats(user_id)

    @classmethod
    def create_fra(cls, user_id: int, title: str, description: str,
                   category_id, monetary_goal, image_url: str = None):
        title = (title or '').strip()
        if len(title) < 3:
            return None, "Title must be at least 3 characters"
        if not description or len(description.strip()) < 10:
            return None, "Description must be at least 10 characters"
        try:
            goal = float(monetary_goal or 0)
            if goal < 0:
                return None, "Monetary goal cannot be negative"
        except (ValueError, TypeError):
            return None, "Monetary goal must be a valid number"
        cat_id = int(category_id) if category_id else None
        fra_id = FRAEntity.create(title, description.strip(), cat_id, goal,
                                  user_id, image_url or None)
        return fra_id, None

    @classmethod
    def list_my_fras(cls, user_id: int, search: str = '', category_id=None,
                     status: str = None, start_date: str = None, end_date: str = None):
        return FRAEntity.find_by_owner(user_id, search, category_id, status, start_date, end_date)

    @classmethod
    def get_fra(cls, fra_id: int, user_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return None, "FRA not found"
        if fra['created_by'] != user_id:
            return None, "Access denied"
        return fra, None

    @classmethod
    def update_fra(cls, fra_id: int, user_id: int, title: str, description: str,
                   category_id, monetary_goal, image_url: str = None):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['created_by'] != user_id:
            return False, "FRA not found"
        if fra['status'] != 'draft':
            return False, "Only draft FRAs can be edited"
        title = (title or '').strip()
        if len(title) < 3:
            return False, "Title must be at least 3 characters"
        if not description or len(description.strip()) < 10:
            return False, "Description must be at least 10 characters"
        try:
            goal = float(monetary_goal or 0)
            if goal < 0:
                return False, "Monetary goal cannot be negative"
        except (ValueError, TypeError):
            return False, "Monetary goal must be a valid number"
        cat_id = int(category_id) if category_id else None
        FRAEntity.update_fields(fra_id, title=title, description=description.strip(),
                                category_id=cat_id, monetary_goal=goal,
                                image_url=image_url or None)
        return True, "FRA updated successfully"

    @classmethod
    def delete_fra(cls, fra_id: int, user_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['created_by'] != user_id:
            return False, "FRA not found"
        if fra['status'] == 'active':
            return False, "Cannot delete an active FRA. Close it first."
        FRAEntity.delete(fra_id)
        return True, f'"{fra["title"]}" has been deleted'

    @classmethod
    def change_status(cls, fra_id: int, user_id: int, new_status: str):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['created_by'] != user_id:
            return False, "FRA not found"
        transitions = {
            'draft': ['pending_approval'],
            'active': ['closed'],
        }
        if new_status not in transitions.get(fra['status'], []):
            return False, f"Cannot transition from '{fra['status']}' to '{new_status}'"
        FRAEntity.update_fields(fra_id, status=new_status)
        msgs = {
            'pending_approval': "FRA submitted for admin review",
            'closed': "FRA has been closed",
        }
        return True, msgs.get(new_status, "Status updated")

    @classmethod
    def get_fra_detail(cls, fra_id: int, user_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['created_by'] != user_id:
            return None, None, None, "FRA not found"
        comments = CommentEntity.list_for_fra(fra_id)
        donations = DonationEntity.find_by_fra(fra_id)
        return fra, comments, donations, None

    @classmethod
    def reply_to_comment(cls, comment_id: int, user_id: int, fra_id: int, content: str):
        content = (content or '').strip()
        if not content:
            return False, "Reply cannot be empty"
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['created_by'] != user_id:
            return False, "Access denied"
        comment = CommentEntity.find_by_id(comment_id)
        if not comment or comment['fra_id'] != fra_id:
            return False, "Comment not found"
        if comment['parent_id'] is not None:
            return False, "Cannot reply to a reply"
        CommentEntity.create(fra_id, user_id, content, parent_id=comment_id)
        return True, "Reply posted"


# ── DoneeController ───────────────────────────────────────────────────────────

class DoneeController(BaseController):

    @classmethod
    def get_dashboard_data(cls, user_id: int) -> dict:
        fras, _ = cls.browse(page=1)
        return {'featured': fras[:6]}

    @classmethod
    def get_dashboard_template(cls) -> str:
        return 'donee/dashboard.html'

    @classmethod
    def browse(cls, search: str = '', category_id=None, page: int = 1):
        return FRAEntity.get_all_active(search, category_id, page)

    @classmethod
    def get_fra_detail(cls, fra_id: int, user_id: int = None):
        FRAEntity.increment_views(fra_id)
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['status'] != 'active':
            return None, None, False, "FRA not found or not currently active"
        comments = CommentEntity.list_for_fra(fra_id)
        is_fav = FRAFavoriteEntity.is_favorited(user_id, fra_id) if user_id else False
        return fra, comments, is_fav, None

    @classmethod
    def toggle_favorite(cls, fra_id: int, user_id: int):
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return None, "FRA not found"
        return FRAFavoriteEntity.toggle(user_id, fra_id), None

    @classmethod
    def get_favorites(cls, user_id: int):
        return FRAEntity.get_favorites_for_user(user_id)

    @classmethod
    def donate(cls, fra_id: int, donor_id: int, amount, message: str = ''):
        try:
            amount = float(amount or 0)
            if amount <= 0:
                return False, "Donation amount must be greater than zero"
        except (ValueError, TypeError):
            return False, "Invalid donation amount"
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return False, "FRA not found"
        if fra['status'] != 'active':
            return False, "This FRA is not currently accepting donations"
        DonationEntity.create(donor_id, fra_id, amount, message or '')
        return True, f"Thank you! Your donation of ${amount:,.2f} to \"{fra['title']}\" was successful."

    @classmethod
    def get_donations(cls, user_id: int, category_id=None,
                      start_date: str = None, end_date: str = None):
        return DonationEntity.find_by_donor(user_id, category_id, start_date, end_date)

    @classmethod
    def add_comment(cls, fra_id: int, user_id: int, content: str):
        content = (content or '').strip()
        if not content:
            return False, "Comment cannot be empty"
        fra = FRAEntity.find_by_id(fra_id)
        if not fra or fra['status'] != 'active':
            return False, "Cannot comment on this FRA"
        CommentEntity.create(fra_id, user_id, content)
        return True, "Comment posted"

    @classmethod
    def report_fra(cls, fra_id: int, reporter_id: int, reason: str):
        reason = (reason or '').strip()
        if len(reason) < 10:
            return False, "Report reason must be at least 10 characters"
        fra = FRAEntity.find_by_id(fra_id)
        if not fra:
            return False, "FRA not found"
        _, err = ReportEntity.create(fra_id, reporter_id, reason)
        if err:
            return False, err
        return True, "Report submitted. Our team will review it."


# ── CategoryController ────────────────────────────────────────────────────────

class CategoryController(BaseController):
    """
    Thin controller so the Boundary layer never imports CategoryEntity directly.
    Satisfies BCE: Boundary → Control → Entity.
    """

    @classmethod
    def list_all(cls):
        return CategoryEntity.get_all()
<<<<<<< HEAD
=======
=======
'''
CONTROL LAYER — Sprint 2: Users, Categories & FRAs
User stories covered: All Sprint 1 + #10,#12-18,#25,#37-39
'''
import re
from werkzeug.security import generate_password_hash, check_password_hash
from entity.models import UserEntity, CategoryEntity, FRAEntity

class BaseController:
    @classmethod
    def _safe(cls, u): return {k:v for k,v in u.items() if k!='password'}
    @classmethod
    def _valid_email(cls, e): return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', e))
    @classmethod
    def _verify_password(cls, stored, provided):
        if stored.startswith(('pbkdf2:','scrypt:')): return check_password_hash(stored,provided)
        return stored==provided

class AuthController(BaseController):
    @classmethod
    def login(cls, email, password):
        if not email or not password: return None,"Email and password are required"
        user=UserEntity.find_by_email(email.strip().lower())
        if not user: return None,"No account found with that email address"
        if not user['is_active']: return None,"This account has been deactivated."
        if not cls._verify_password(user['password'],password): return None,"Incorrect password"
        UserEntity.record_login(user['id']); return cls._safe(user),None
    @classmethod
    def register(cls, full_name, email, password, confirm, role='donee'):
        full_name=(full_name or '').strip(); email=(email or '').strip().lower()
        if len(full_name)<2: return None,"Full name must be at least 2 characters"
        if not cls._valid_email(email): return None,"Please enter a valid email address"
        if not password or len(password)<6: return None,"Password must be at least 6 characters"
        if password!=confirm: return None,"Passwords do not match"
        if role not in ('fundraiser','donee'): role='donee'
        uid,err=UserEntity.create(full_name,email,generate_password_hash(password),role)
        if err: return None,err
        return cls._safe(UserEntity.find_by_id(uid)),None

class ProfileController(BaseController):
    @classmethod
    def get(cls,uid):
        u=UserEntity.find_by_id(uid); return cls._safe(u) if u else None
    @classmethod
    def update(cls,uid,full_name,bio,phone,address):
        full_name=(full_name or '').strip()
        if len(full_name)<2: return False,"Full name must be at least 2 characters"
        UserEntity.update(uid,full_name=full_name,bio=bio or '',phone=phone or '',address=address or '')
        return True,"Profile updated successfully"
    @classmethod
    def change_password(cls,uid,cur,new,confirm):
        u=UserEntity.find_by_id(uid)
        if not u: return False,"User not found"
        if not cls._verify_password(u['password'],cur): return False,"Current password is incorrect"
        if not new or len(new)<6: return False,"New password must be at least 6 characters"
        if new!=confirm: return False,"New passwords do not match"
        UserEntity.update_password(uid,generate_password_hash(new)); return True,"Password changed successfully"

class AdminController(BaseController):
    @classmethod
    def get_dashboard_data(cls,uid): return {'stats':cls.dashboard_stats()}
    @classmethod
    def get_dashboard_template(cls): return 'admin/dashboard.html'
    @classmethod
    def dashboard_stats(cls):
        users,total=UserEntity.search(); fra_stats=FRAEntity.platform_stats()
        return {'total_users':total,'active_users':sum(1 for u in users if u['is_active']),
                'role_counts':UserEntity.count_by_role(),'new_users_30d':UserEntity.count_new(30),
                'fra_stats':fra_stats,'pending_fras':fra_stats.get('pending',0)}
    @classmethod
    def list_users(cls,search='',role=None,is_active=None,page=1):
        u,t=UserEntity.search(search,role,is_active,page); return [cls._safe(x) for x in u],t
    @classmethod
    def get_user(cls,uid):
        u=UserEntity.find_by_id(uid)
        if not u: return None,"User not found"
        return cls._safe(u),None
    @classmethod
    def create_user(cls,fn,email,pw,role):
        fn=(fn or '').strip(); email=(email or '').strip().lower()
        if len(fn)<2: return None,"Full name must be at least 2 characters"
        if not cls._valid_email(email): return None,"Invalid email address"
        if not pw or len(pw)<6: return None,"Password must be at least 6 characters"
        if role not in ('admin','fundraiser','donee'): return None,"Invalid role"
        return UserEntity.create(fn,email,generate_password_hash(pw),role)
    @classmethod
    def update_user(cls,uid,fn,email,role,phone,addr,bio):
        if not UserEntity.find_by_id(uid): return False,"User not found"
        up={}
        if fn and len(fn.strip())>=2: up['full_name']=fn.strip()
        if email and cls._valid_email(email.strip().lower()): up['email']=email.strip().lower()
        if role and role in ('admin','fundraiser','donee'): up['role']=role
        if phone is not None: up['phone']=phone
        if addr is not None: up['address']=addr
        if bio is not None: up['bio']=bio
        UserEntity.update(uid,**up); return True,"User updated successfully"
    @classmethod
    def deactivate_user(cls,uid,rid):
        if uid==rid: return False,"You cannot deactivate your own account"
        u=UserEntity.find_by_id(uid)
        if not u: return False,"User not found"
        if u['role']=='admin': return False,"Cannot deactivate another admin account"
        UserEntity.update(uid,is_active=0); return True,f"{u['full_name']}'s account has been deactivated"
    @classmethod
    def reactivate_user(cls,uid):
        u=UserEntity.find_by_id(uid)
        if not u: return False,"User not found"
        UserEntity.update(uid,is_active=1); return True,f"{u['full_name']}'s account has been reactivated"
    @classmethod
    def delete_user(cls,uid,rid):
        if uid==rid: return False,"You cannot delete your own account"
        u=UserEntity.find_by_id(uid)
        if not u: return False,"User not found"
        if u['role']=='admin': return False,"Cannot delete an admin account"
        name=u['full_name']; UserEntity.delete(uid); return True,f"{name}'s account has been permanently deleted"
    @classmethod
    def reset_password(cls,uid,pw,rid):
        if uid==rid: return False,"Use Change Password to update your own password"
        if not pw or len(pw)<6: return False,"Password must be at least 6 characters"
        u=UserEntity.find_by_id(uid)
        if not u: return False,"User not found"
        UserEntity.update_password(uid,generate_password_hash(pw)); return True,f"Password reset for {u['full_name']}"
    @classmethod
    def list_categories(cls,search=''): return CategoryEntity.search(search)
    @classmethod
    def create_category(cls,name,desc=''):
        name=(name or '').strip()
        if len(name)<2: return None,"Category name must be at least 2 characters"
        return CategoryEntity.create(name,desc or '')
    @classmethod
    def update_category(cls,cid,name,desc):
        if not CategoryEntity.find_by_id(cid): return False,"Category not found"
        name=(name or '').strip()
        if name and len(name)<2: return False,"Category name must be at least 2 characters"
        ok,err=CategoryEntity.update(cid,name or None,desc)
        return (True,"Category updated") if ok else (False,err)
    @classmethod
    def delete_category(cls,cid):
        cat=CategoryEntity.find_by_id(cid)
        if not cat: return False,"Category not found"
        CategoryEntity.delete(cid); return True,f"Category '{cat['name']}' deleted"
    @classmethod
    def list_fras(cls,search='',status=None,cat_id=None,page=1):
        return FRAEntity.get_all(search,status,cat_id,page)
    @classmethod
    def list_pending(cls): return FRAEntity.get_pending_approval()
    @classmethod
    def approve_fra(cls,fid):
        fra=FRAEntity.find_by_id(fid)
        if not fra: return False,"FRA not found"
        if fra['status']!='pending_approval': return False,"FRA is not pending approval"
        FRAEntity.update_fields(fid,status='active')
        return True,f'"{fra["title"]}" approved and is now live'
    @classmethod
    def reject_fra(cls,fid):
        fra=FRAEntity.find_by_id(fid)
        if not fra: return False,"FRA not found"
        if fra['status']!='pending_approval': return False,"FRA is not pending approval"
        FRAEntity.update_fields(fid,status='draft')
        return True,f'"{fra["title"]}" rejected and returned to draft'
    @classmethod
    def force_close_fra(cls,fid):
        fra=FRAEntity.find_by_id(fid)
        if not fra: return False,"FRA not found"
        FRAEntity.update_fields(fid,status='closed'); return True,f'"{fra["title"]}" closed'

class FundraiserController(BaseController):
    @classmethod
    def get_dashboard_data(cls,uid):
        return {'stats':cls.get_stats(uid),'recent':cls.list_my_fras(uid)[:5]}
    @classmethod
    def get_dashboard_template(cls): return 'fundraiser/dashboard.html'
    @classmethod
    def get_stats(cls,uid): return FRAEntity.owner_stats(uid)
    @classmethod
    def create_fra(cls,uid,title,desc,cat_id,goal,image_url=None):
        title=(title or '').strip()
        if len(title)<3: return None,"Title must be at least 3 characters"
        if not desc or len(desc.strip())<10: return None,"Description must be at least 10 characters"
        try:
            goal=float(goal or 0)
            if goal<0: return None,"Monetary goal cannot be negative"
        except: return None,"Monetary goal must be a valid number"
        fid=FRAEntity.create(title,desc.strip(),int(cat_id) if cat_id else None,goal,uid,image_url or None)
        return fid,None
    @classmethod
    def list_my_fras(cls,uid,search='',cat_id=None,status=None,start=None,end=None):
        return FRAEntity.find_by_owner(uid,search,cat_id,status,start,end)
    @classmethod
    def get_fra(cls,fid,uid):
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['created_by']!=uid: return None,"FRA not found"
        return fra,None
    @classmethod
    def update_fra(cls,fid,uid,title,desc,cat_id,goal,image_url=None):
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['created_by']!=uid: return False,"FRA not found"
        if fra['status']!='draft': return False,"Only draft FRAs can be edited"
        title=(title or '').strip()
        if len(title)<3: return False,"Title must be at least 3 characters"
        if not desc or len(desc.strip())<10: return False,"Description must be at least 10 characters"
        try:
            goal=float(goal or 0)
            if goal<0: return False,"Monetary goal cannot be negative"
        except: return False,"Monetary goal must be a valid number"
        FRAEntity.update_fields(fid,title=title,description=desc.strip(),
            category_id=int(cat_id) if cat_id else None,monetary_goal=goal,image_url=image_url or None)
        return True,"FRA updated successfully"
    @classmethod
    def delete_fra(cls,fid,uid):
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['created_by']!=uid: return False,"FRA not found"
        if fra['status']=='active': return False,"Cannot delete an active FRA. Close it first."
        FRAEntity.delete(fid); return True,f'"{fra["title"]}" deleted'
    @classmethod
    def change_status(cls,fid,uid,new_status):
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['created_by']!=uid: return False,"FRA not found"
        transitions={'draft':['pending_approval'],'active':['closed']}
        if new_status not in transitions.get(fra['status'],[]):
            return False,f"Cannot transition from '{fra['status']}' to '{new_status}'"
        FRAEntity.update_fields(fid,status=new_status)
        msgs={'pending_approval':'FRA submitted for admin review','closed':'FRA closed'}
        return True,msgs.get(new_status,'Status updated')
    @classmethod
    def get_fra_detail(cls,fid,uid):
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['created_by']!=uid: return None,None,"FRA not found"
        return fra,[],None

class DoneeController(BaseController):
    @classmethod
    def get_dashboard_data(cls,uid):
        fras,_=cls.browse(); return {'featured':fras[:6]}
    @classmethod
    def get_dashboard_template(cls): return 'donee/dashboard.html'
    @classmethod
    def browse(cls,search='',cat_id=None,page=1):
        return FRAEntity.get_all_active(search,cat_id,page)
    @classmethod
    def get_fra_detail(cls,fid,uid=None):
        FRAEntity.increment_views(fid)
        fra=FRAEntity.find_by_id(fid)
        if not fra or fra['status']!='active': return None,[],False,"FRA not found or not active"
        return fra,[],False,None

class CategoryController(BaseController):
    @classmethod
    def list_all(cls): return CategoryEntity.get_all()
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
