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
