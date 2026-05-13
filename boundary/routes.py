<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
"""
BOUNDARY LAYER — BCE Architecture
HTTP interface only. Renders Jinja2 templates, manages sessions, flashes messages.
All logic delegated to Control layer. Zero business rules here.

"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import (Flask, render_template, request, session,
                   redirect, url_for, flash)
from functools import wraps
from entity.models import init_db   # init_db is bootstrap — acceptable direct import
from control.controllers import (
    AuthController, ProfileController, AdminController,
    FundraiserController, DoneeController, CategoryController
)

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.secret_key = os.environ.get('SECRET_KEY', 'tacofundme-secret-key-2024-xyz')
init_db()


# ── Decorators ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

<<<<<<< HEAD
=======
=======
'''BOUNDARY LAYER — Sprint 2: Users, Categories & FRAs'''
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from flask import Flask,render_template,request,session,redirect,url_for,flash
from functools import wraps
from entity.models import init_db
from control.controllers import (AuthController,ProfileController,AdminController,
                                  FundraiserController,DoneeController,CategoryController)

app=Flask(__name__,static_folder='../static',template_folder='../templates')
app.secret_key=os.environ.get('SECRET_KEY','sprint2-secret')
init_db()

def login_required(f):
    @wraps(f)
    def d(*a,**kw):
        if 'user_id' not in session:
            flash('Please log in.','warning'); return redirect(url_for('login'))
        return f(*a,**kw)
    return d
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

def admin_required(f):
    @wraps(f)
    @login_required
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

<<<<<<< HEAD
=======
=======
    def d(*a,**kw):
        if session.get('role')!='admin':
            flash('Admin access required.','danger'); return redirect(url_for('dashboard'))
        return f(*a,**kw)
    return d
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

def fundraiser_required(f):
    @wraps(f)
    @login_required
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    def decorated(*args, **kwargs):
        if session.get('role') != 'fundraiser':
            flash('Fundraiser access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


def donee_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if session.get('role') not in ('donee', 'donor', 'volunteer'):
            flash('Donee access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user, err = AuthController.login(email, password)
        if err:
            flash(err, 'danger')
            return render_template('auth/login.html', email=email)
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['name'] = user['full_name']
        flash(f"Welcome back, {user['full_name']}!", 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user, err = AuthController.register(
            request.form.get('full_name', ''),
            request.form.get('email', ''),
            request.form.get('password', ''),
            request.form.get('confirm_password', ''),
            request.form.get('role', 'donee'),
        )
        if err:
            flash(err, 'danger')
            return render_template('auth/register.html',
                                   full_name=request.form.get('full_name'),
                                   email=request.form.get('email'),
                                   role=request.form.get('role', 'donee'))
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['name'] = user['full_name']
        flash(f"Welcome to TACOFundMe, {user['full_name']}!", 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('login'))


# ── Dashboard (polymorphic dispatch) ──────────────────────────────────────────

# Maps each role to the controller that knows how to build its dashboard.
# Adding a new role only requires adding one entry here — no if/elif editing.
_DASHBOARD_CONTROLLERS = {
    'admin':      AdminController,
    'fundraiser': FundraiserController,
    'donee':      DoneeController,
    'donor':      DoneeController,
    'volunteer':  DoneeController,
}

<<<<<<< HEAD
=======
=======
    def d(*a,**kw):
        if session.get('role')!='fundraiser':
            flash('Fundraiser access required.','danger'); return redirect(url_for('dashboard'))
        return f(*a,**kw)
    return d

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        user,err=AuthController.login(request.form.get('email','').strip(),request.form.get('password',''))
        if err: flash(err,'danger'); return render_template('auth/login.html',email=request.form.get('email'))
        session.update({'user_id':user['id'],'role':user['role'],'name':user['full_name']})
        flash(f"Welcome back, {user['full_name']}!",'success'); return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        user,err=AuthController.register(request.form.get('full_name',''),request.form.get('email',''),
            request.form.get('password',''),request.form.get('confirm_password',''),request.form.get('role','donee'))
        if err:
            flash(err,'danger')
            return render_template('auth/register.html',full_name=request.form.get('full_name'),
                email=request.form.get('email'),role=request.form.get('role','donee'))
        session.update({'user_id':user['id'],'role':user['role'],'name':user['full_name']})
        flash(f"Welcome to TACOFundMe, {user['full_name']}!",'success'); return redirect(url_for('dashboard'))
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear(); flash('You have been signed out.','info'); return redirect(url_for('login'))

_DASH={'admin':AdminController,'fundraiser':FundraiserController,'donee':DoneeController,'donor':DoneeController}
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/dashboard')
@login_required
def dashboard():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    ctrl = _DASHBOARD_CONTROLLERS.get(session.get('role'), DoneeController)
    data = ctrl.get_dashboard_data(session['user_id'])
    return render_template(ctrl.get_dashboard_template(), **data)


# ── Profile ───────────────────────────────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', 'update')
        if action == 'update':
            ok, msg = ProfileController.update(
                session['user_id'],
                request.form.get('full_name'),
                request.form.get('bio'),
                request.form.get('phone'),
                request.form.get('address'),
            )
            if ok:
                session['name'] = request.form.get('full_name', session['name'])
        else:
            ok, msg = ProfileController.change_password(
                session['user_id'],
                request.form.get('current_password', ''),
                request.form.get('new_password', ''),
                request.form.get('confirm_new', ''),
            )
        flash(msg, 'success' if ok else 'danger')
        return redirect(url_for('profile'))
    user = ProfileController.get(session['user_id'])
    return render_template('common/profile.html', user=user)


# ── Admin: Users ──────────────────────────────────────────────────────────────
<<<<<<< HEAD
=======
=======
    ctrl=_DASH.get(session.get('role'),DoneeController)
    return render_template(ctrl.get_dashboard_template(),**ctrl.get_dashboard_data(session['user_id']))

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        if request.form.get('action')=='update':
            ok,msg=ProfileController.update(session['user_id'],request.form.get('full_name'),
                request.form.get('bio'),request.form.get('phone'),request.form.get('address'))
            if ok: session['name']=request.form.get('full_name',session['name'])
        else:
            ok,msg=ProfileController.change_password(session['user_id'],
                request.form.get('current_password',''),request.form.get('new_password',''),request.form.get('confirm_new',''))
        flash(msg,'success' if ok else 'danger'); return redirect(url_for('profile'))
    return render_template('common/profile.html',user=ProfileController.get(session['user_id']))
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/admin/users')
@admin_required
def admin_users():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    search = request.args.get('q', '')
    role_f = request.args.get('role', '')
    active_f = request.args.get('active', '')
    page = max(1, request.args.get('page', 1, type=int))
    is_active = None
    if active_f == '1': is_active = True
    elif active_f == '0': is_active = False
    users, total = AdminController.list_users(search, role_f or None, is_active, page)
    pages = max(1, (total + 19) // 20)
    return render_template('admin/users.html',
                           users=users, total=total, pages=pages,
                           search=search, role_f=role_f, active_f=active_f, page=page)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    if request.method == 'POST':
        uid, err = AdminController.create_user(
            request.form.get('full_name', ''),
            request.form.get('email', ''),
            request.form.get('password', ''),
            request.form.get('role', 'donee'),
        )
        if err:
            flash(err, 'danger')
            return render_template('admin/user_create.html', fd=request.form)
        flash('User account created successfully.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_create.html', fd={})


@app.route('/admin/users/<int:uid>', methods=['GET', 'POST'])
@admin_required
def admin_user_detail(uid):
    user, err = AdminController.get_user(uid)
    if err:
        flash(err, 'danger')
        return redirect(url_for('admin_users'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update':
            ok, msg = AdminController.update_user(
                uid,
                request.form.get('full_name'),
                request.form.get('email'),
                request.form.get('role'),
                request.form.get('phone'),
                request.form.get('address'),
                request.form.get('bio'),
            )
        elif action == 'deactivate':
            ok, msg = AdminController.deactivate_user(uid, session['user_id'])
        elif action == 'reactivate':
            ok, msg = AdminController.reactivate_user(uid)
        elif action == 'reset_password':
            ok, msg = AdminController.reset_password(
                uid, request.form.get('new_password', ''), session['user_id']
            )
        elif action == 'delete':
            ok, msg = AdminController.delete_user(uid, session['user_id'])
            flash(msg, 'success' if ok else 'danger')
            if ok:
                return redirect(url_for('admin_users'))
            return redirect(url_for('admin_user_detail', uid=uid))
        else:
            ok, msg = False, "Unknown action"
        flash(msg, 'success' if ok else 'danger')
        return redirect(url_for('admin_user_detail', uid=uid))
    return render_template('admin/user_detail.html', user=user)


# ── Admin: Categories ─────────────────────────────────────────────────────────
<<<<<<< HEAD
=======
=======
    s=request.args.get('q',''); rf=request.args.get('role',''); af=request.args.get('active','')
    page=max(1,request.args.get('page',1,type=int))
    ia=True if af=='1' else (False if af=='0' else None)
    users,total=AdminController.list_users(s,rf or None,ia,page)
    return render_template('admin/users.html',users=users,total=total,pages=max(1,(total+19)//20),
        search=s,role_f=rf,active_f=af,page=page)

@app.route('/admin/users/create',methods=['GET','POST'])
@admin_required
def admin_create_user():
    if request.method=='POST':
        uid,err=AdminController.create_user(request.form.get('full_name',''),request.form.get('email',''),
            request.form.get('password',''),request.form.get('role','donee'))
        if err: flash(err,'danger'); return render_template('admin/user_create.html',fd=request.form)
        flash('User account created successfully.','success'); return redirect(url_for('admin_users'))
    return render_template('admin/user_create.html',fd={})

@app.route('/admin/users/<int:uid>',methods=['GET','POST'])
@admin_required
def admin_user_detail(uid):
    user,err=AdminController.get_user(uid)
    if err: flash(err,'danger'); return redirect(url_for('admin_users'))
    if request.method=='POST':
        a=request.form.get('action')
        if a=='update': ok,msg=AdminController.update_user(uid,request.form.get('full_name'),request.form.get('email'),request.form.get('role'),request.form.get('phone'),request.form.get('address'),request.form.get('bio'))
        elif a=='deactivate': ok,msg=AdminController.deactivate_user(uid,session['user_id'])
        elif a=='reactivate': ok,msg=AdminController.reactivate_user(uid)
        elif a=='reset_password': ok,msg=AdminController.reset_password(uid,request.form.get('new_password',''),session['user_id'])
        elif a=='delete':
            ok,msg=AdminController.delete_user(uid,session['user_id'])
            flash(msg,'success' if ok else 'danger')
            return redirect(url_for('admin_users') if ok else url_for('admin_user_detail',uid=uid))
        else: ok,msg=False,"Unknown action"
        flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_user_detail',uid=uid))
    return render_template('admin/user_detail.html',user=user)
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/admin/categories')
@admin_required
def admin_categories():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    search = request.args.get('q', '')
    cats = AdminController.list_categories(search)
    return render_template('admin/categories.html', categories=cats, search=search)


@app.route('/admin/categories/create', methods=['POST'])
@admin_required
def admin_create_category():
    cid, err = AdminController.create_category(
        request.form.get('name', ''),
        request.form.get('description', ''),
    )
    flash('Category created.' if not err else err, 'success' if not err else 'danger')
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/<int:cid>/edit', methods=['POST'])
@admin_required
def admin_edit_category(cid):
    ok, msg = AdminController.update_category(
        cid,
        request.form.get('name', ''),
        request.form.get('description', ''),
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/<int:cid>/delete', methods=['POST'])
@admin_required
def admin_delete_category(cid):
    ok, msg = AdminController.delete_category(cid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_categories'))


# ── Admin: FRAs ───────────────────────────────────────────────────────────────
<<<<<<< HEAD
=======
=======
    s=request.args.get('q','')
    return render_template('admin/categories.html',categories=AdminController.list_categories(s),search=s)

@app.route('/admin/categories/create',methods=['POST'])
@admin_required
def admin_create_category():
    cid,err=AdminController.create_category(request.form.get('name',''),request.form.get('description',''))
    flash('Category created.' if not err else err,'success' if not err else 'danger')
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/<int:cid>/edit',methods=['POST'])
@admin_required
def admin_edit_category(cid):
    ok,msg=AdminController.update_category(cid,request.form.get('name',''),request.form.get('description',''))
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_categories'))

@app.route('/admin/categories/<int:cid>/delete',methods=['POST'])
@admin_required
def admin_delete_category(cid):
    ok,msg=AdminController.delete_category(cid)
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_categories'))
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/admin/fras')
@admin_required
def admin_fras():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    cat_id = request.args.get('category_id', '')
    page = max(1, request.args.get('page', 1, type=int))
    fras, total = AdminController.list_fras(
        search, status or None, int(cat_id) if cat_id else None, page
    )
    pages = max(1, (total + 19) // 20)
    cats = CategoryController.list_all()   # Boundary → Control → Entity
    return render_template('admin/fras.html',
                           fras=fras, total=total, pages=pages,
                           search=search, status=status, cat_id=cat_id,
                           categories=cats, page=page)

<<<<<<< HEAD
=======
=======
    s=request.args.get('q',''); st=request.args.get('status',''); ci=request.args.get('category_id','')
    page=max(1,request.args.get('page',1,type=int))
    fras,total=AdminController.list_fras(s,st or None,int(ci) if ci else None,page)
    return render_template('admin/fras.html',fras=fras,total=total,pages=max(1,(total+19)//20),
        search=s,status=st,cat_id=ci,categories=CategoryController.list_all(),page=page)
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/admin/fras/approvals')
@admin_required
def admin_approvals():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    pending = AdminController.list_pending()
    return render_template('admin/approvals.html', pending=pending)


@app.route('/admin/fras/<int:fra_id>/approve', methods=['POST'])
@admin_required
def admin_approve_fra(fra_id):
    ok, msg = AdminController.approve_fra(fra_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_approvals'))


@app.route('/admin/fras/<int:fra_id>/reject', methods=['POST'])
@admin_required
def admin_reject_fra(fra_id):
    ok, msg = AdminController.reject_fra(fra_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_approvals'))


@app.route('/admin/fras/<int:fra_id>/close', methods=['POST'])
@admin_required
def admin_close_fra(fra_id):
    ok, msg = AdminController.force_close_fra(fra_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_fras'))


# ── Admin: Reports ────────────────────────────────────────────────────────────

@app.route('/admin/reports')
@admin_required
def admin_reports():
    period = request.args.get('period', 'monthly')
    if period not in ('daily', 'weekly', 'monthly'):
        period = 'monthly'
    keyword  = request.args.get('q', '').strip()
    r_status = request.args.get('r_status', '')
    r_start  = request.args.get('r_start', '')
    r_end    = request.args.get('r_end', '')
    report      = AdminController.generate_report(period)
    fra_reports = AdminController.list_reports(
        keyword or None, r_status or None,
        r_start or None, r_end or None,
    )
    return render_template('admin/reports.html', report=report,
                           period=period, fra_reports=fra_reports,
                           keyword=keyword, r_status=r_status,
                           r_start=r_start, r_end=r_end)


@app.route('/admin/reports/<int:rid>/resolve', methods=['POST'])
@admin_required
def admin_resolve_report(rid):
    ok, msg = AdminController.resolve_report(rid)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin_reports'))


# ── Fundraiser ────────────────────────────────────────────────────────────────
<<<<<<< HEAD
=======
=======
    return render_template('admin/approvals.html',pending=AdminController.list_pending())

@app.route('/admin/fras/<int:fid>/approve',methods=['POST'])
@admin_required
def admin_approve_fra(fid):
    ok,msg=AdminController.approve_fra(fid)
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_approvals'))

@app.route('/admin/fras/<int:fid>/reject',methods=['POST'])
@admin_required
def admin_reject_fra(fid):
    ok,msg=AdminController.reject_fra(fid)
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_approvals'))

@app.route('/admin/fras/<int:fid>/close',methods=['POST'])
@admin_required
def admin_close_fra(fid):
    ok,msg=AdminController.force_close_fra(fid)
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('admin_fras'))
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/fundraiser/fras')
@fundraiser_required
def fr_fras():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    search = request.args.get('q', '')
    cat_id = request.args.get('category_id', '')
    status = request.args.get('status', '')
    start = request.args.get('start_date', '')
    end = request.args.get('end_date', '')
    fras = FundraiserController.list_my_fras(
        session['user_id'], search,
        int(cat_id) if cat_id else None,
        status or None, start or None, end or None
    )
    cats = CategoryController.list_all()
    return render_template('fundraiser/fras.html', fras=fras, categories=cats,
                           search=search, cat_id=cat_id, status=status,
                           start=start, end=end)


@app.route('/fundraiser/fras/create', methods=['GET', 'POST'])
@fundraiser_required
def fr_create_fra():
    cats = CategoryController.list_all()
    if request.method == 'POST':
        fra_id, err = FundraiserController.create_fra(
            session['user_id'],
            request.form.get('title', ''),
            request.form.get('description', ''),
            request.form.get('category_id') or None,
            request.form.get('monetary_goal', 0),
            request.form.get('image_url') or None,
        )
        if err:
            flash(err, 'danger')
            return render_template('fundraiser/fra_form.html',
                                   categories=cats, fd=request.form, action='create')
        flash('FRA created as draft.', 'success')
        return redirect(url_for('fr_fra_detail', fra_id=fra_id))
    return render_template('fundraiser/fra_form.html',
                           categories=cats, fd={}, action='create')


@app.route('/fundraiser/fras/<int:fra_id>')
@fundraiser_required
def fr_fra_detail(fra_id):
    fra, comments, donations, err = FundraiserController.get_fra_detail(
        fra_id, session['user_id']
    )
    if err:
        flash(err, 'danger')
        return redirect(url_for('fr_fras'))
    return render_template('fundraiser/fra_detail.html',
                           fra=fra, comments=comments, donations=donations)


@app.route('/fundraiser/fras/<int:fra_id>/edit', methods=['GET', 'POST'])
@fundraiser_required
def fr_edit_fra(fra_id):
    fra, err = FundraiserController.get_fra(fra_id, session['user_id'])
    if err:
        flash(err, 'danger')
        return redirect(url_for('fr_fras'))
    if fra['status'] != 'draft':
        flash('Only draft FRAs can be edited.', 'warning')
        return redirect(url_for('fr_fra_detail', fra_id=fra_id))
    cats = CategoryController.list_all()
    if request.method == 'POST':
        ok, msg = FundraiserController.update_fra(
            fra_id, session['user_id'],
            request.form.get('title', ''),
            request.form.get('description', ''),
            request.form.get('category_id') or None,
            request.form.get('monetary_goal', 0),
            request.form.get('image_url') or None,
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('fr_fra_detail', fra_id=fra_id))
    return render_template('fundraiser/fra_form.html',
                           fra=fra, categories=cats,
                           fd={k: fra.get(k) for k in
                               ['title', 'description', 'category_id',
                                'monetary_goal', 'image_url']},
                           action='edit')


@app.route('/fundraiser/fras/<int:fra_id>/status', methods=['POST'])
@fundraiser_required
def fr_change_status(fra_id):
    ok, msg = FundraiserController.change_status(
        fra_id, session['user_id'], request.form.get('status', '')
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fr_fra_detail', fra_id=fra_id))


@app.route('/fundraiser/fras/<int:fra_id>/delete', methods=['POST'])
@fundraiser_required
def fr_delete_fra(fra_id):
    ok, msg = FundraiserController.delete_fra(fra_id, session['user_id'])
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fr_fras') if ok else url_for('fr_fra_detail', fra_id=fra_id))


@app.route('/fundraiser/fras/<int:fra_id>/reply', methods=['POST'])
@fundraiser_required
def fr_reply_comment(fra_id):
    ok, msg = FundraiserController.reply_to_comment(
        request.form.get('comment_id', type=int),
        session['user_id'], fra_id,
        request.form.get('content', ''),
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fr_fra_detail', fra_id=fra_id))


# ── Donee: Browse ─────────────────────────────────────────────────────────────
<<<<<<< HEAD
=======
=======
    s=request.args.get('q',''); ci=request.args.get('category_id','')
    st=request.args.get('status',''); start=request.args.get('start_date',''); end=request.args.get('end_date','')
    fras=FundraiserController.list_my_fras(session['user_id'],s,int(ci) if ci else None,st or None,start or None,end or None)
    return render_template('fundraiser/fras.html',fras=fras,categories=CategoryController.list_all(),
        search=s,cat_id=ci,status=st,start=start,end=end)

@app.route('/fundraiser/fras/create',methods=['GET','POST'])
@fundraiser_required
def fr_create_fra():
    cats=CategoryController.list_all()
    if request.method=='POST':
        fid,err=FundraiserController.create_fra(session['user_id'],request.form.get('title',''),
            request.form.get('description',''),request.form.get('category_id') or None,
            request.form.get('monetary_goal',0),request.form.get('image_url') or None)
        if err: flash(err,'danger'); return render_template('fundraiser/fra_form.html',categories=cats,fd=request.form,action='create')
        flash('FRA created as draft.','success'); return redirect(url_for('fr_fra_detail',fid=fid))
    return render_template('fundraiser/fra_form.html',categories=cats,fd={},action='create')

@app.route('/fundraiser/fras/<int:fid>')
@fundraiser_required
def fr_fra_detail(fid):
    fra,comments,err=FundraiserController.get_fra_detail(fid,session['user_id'])
    if err: flash(err,'danger'); return redirect(url_for('fr_fras'))
    return render_template('fundraiser/fra_detail.html',fra=fra,comments=comments,donations=[])

@app.route('/fundraiser/fras/<int:fid>/edit',methods=['GET','POST'])
@fundraiser_required
def fr_edit_fra(fid):
    fra,err=FundraiserController.get_fra(fid,session['user_id'])
    if err: flash(err,'danger'); return redirect(url_for('fr_fras'))
    if fra['status']!='draft': flash('Only draft FRAs can be edited.','warning'); return redirect(url_for('fr_fra_detail',fid=fid))
    cats=CategoryController.list_all()
    if request.method=='POST':
        ok,msg=FundraiserController.update_fra(fid,session['user_id'],request.form.get('title',''),
            request.form.get('description',''),request.form.get('category_id') or None,
            request.form.get('monetary_goal',0),request.form.get('image_url') or None)
        flash(msg,'success' if ok else 'danger')
        if ok: return redirect(url_for('fr_fra_detail',fid=fid))
    return render_template('fundraiser/fra_form.html',fra=fra,categories=cats,
        fd={k:fra.get(k) for k in ['title','description','category_id','monetary_goal','image_url']},action='edit')

@app.route('/fundraiser/fras/<int:fid>/status',methods=['POST'])
@fundraiser_required
def fr_change_status(fid):
    ok,msg=FundraiserController.change_status(fid,session['user_id'],request.form.get('status',''))
    flash(msg,'success' if ok else 'danger'); return redirect(url_for('fr_fra_detail',fid=fid))

@app.route('/fundraiser/fras/<int:fid>/delete',methods=['POST'])
@fundraiser_required
def fr_delete_fra(fid):
    ok,msg=FundraiserController.delete_fra(fid,session['user_id'])
    flash(msg,'success' if ok else 'danger')
    return redirect(url_for('fr_fras') if ok else url_for('fr_fra_detail',fid=fid))
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

@app.route('/browse')
@login_required
def browse():
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    search = request.args.get('q', '')
    cat_id = request.args.get('category_id', '')
    page = max(1, request.args.get('page', 1, type=int))
    fras, total = DoneeController.browse(
        search, int(cat_id) if cat_id else None, page
    )
    total_pages = max(1, (total + 11) // 12)
    cats = CategoryController.list_all()
    return render_template('donee/browse.html',
                           fras=fras, total=total, page=page,
                           total_pages=total_pages, categories=cats,
                           search=search, cat_id=cat_id)


@app.route('/browse/<int:fra_id>')
@login_required
def fra_detail(fra_id):
    user_id = session.get('user_id')
    fra, comments, is_fav, err = DoneeController.get_fra_detail(fra_id, user_id)
    if err:
        flash(err, 'danger')
        return redirect(url_for('browse'))
    return render_template('donee/fra_detail.html',
                           fra=fra, comments=comments, is_fav=is_fav)


@app.route('/browse/<int:fra_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(fra_id):
    if session.get('role') not in ('donee', 'donor', 'volunteer'):
        flash('Only donees can save favourites.', 'warning')
        return redirect(url_for('fra_detail', fra_id=fra_id))
    added, err = DoneeController.toggle_favorite(fra_id, session['user_id'])
    if err:
        flash(err, 'danger')
    else:
        flash('Saved to favourites.' if added else 'Removed from favourites.', 'success')
    return redirect(url_for('fra_detail', fra_id=fra_id))


@app.route('/browse/<int:fra_id>/donate', methods=['POST'])
@login_required
def donate(fra_id):
    if session.get('role') not in ('donee', 'donor', 'volunteer'):
        flash('Only donees can donate.', 'warning')
        return redirect(url_for('fra_detail', fra_id=fra_id))
    ok, msg = DoneeController.donate(
        fra_id, session['user_id'],
        request.form.get('amount', 0),
        request.form.get('message', ''),
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fra_detail', fra_id=fra_id))


@app.route('/browse/<int:fra_id>/comment', methods=['POST'])
@login_required
def add_comment(fra_id):
    if session.get('role') not in ('donee', 'donor', 'volunteer'):
        flash('Only donees can leave comments.', 'warning')
        return redirect(url_for('fra_detail', fra_id=fra_id))
    ok, msg = DoneeController.add_comment(
        fra_id, session['user_id'], request.form.get('content', '')
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fra_detail', fra_id=fra_id))


@app.route('/browse/<int:fra_id>/report', methods=['POST'])
@login_required
def report_fra(fra_id):
    if session.get('role') not in ('donee', 'donor', 'volunteer'):
        flash('Only donees can report FRAs.', 'warning')
        return redirect(url_for('fra_detail', fra_id=fra_id))
    ok, msg = DoneeController.report_fra(
        fra_id, session['user_id'], request.form.get('reason', '')
    )
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fra_detail', fra_id=fra_id))


@app.route('/favourites')
@donee_required
def favourites():
    fras = DoneeController.get_favorites(session['user_id'])
    return render_template('donee/favourites.html', fras=fras)


@app.route('/favourites/<int:fra_id>/remove', methods=['POST'])
@donee_required
def remove_favourite(fra_id):
    DoneeController.toggle_favorite(fra_id, session['user_id'])
    flash('Removed from favourites.', 'info')
    return redirect(url_for('favourites'))


@app.route('/donations')
@donee_required
def my_donations():
    cat_id = request.args.get('category_id', '')
    start = request.args.get('start_date', '')
    end = request.args.get('end_date', '')
    donations = DoneeController.get_donations(
        session['user_id'],
        int(cat_id) if cat_id else None,
        start or None, end or None
    )
    cats = CategoryController.list_all()
    total = sum(d['amount'] for d in donations)
    return render_template('donee/donations.html',
                           donations=donations, categories=cats,
                           cat_id=cat_id, start=start, end=end,
                           total=total)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
<<<<<<< HEAD
=======
=======
    s=request.args.get('q',''); ci=request.args.get('category_id',''); page=max(1,request.args.get('page',1,type=int))
    fras,total=DoneeController.browse(s,int(ci) if ci else None,page)
    return render_template('donee/browse.html',fras=fras,total=total,page=page,
        total_pages=max(1,(total+11)//12),categories=CategoryController.list_all(),search=s,cat_id=ci)

@app.route('/browse/<int:fid>')
@login_required
def fra_detail(fid):
    fra,comments,is_fav,err=DoneeController.get_fra_detail(fid,session.get('user_id'))
    if err: flash(err,'danger'); return redirect(url_for('browse'))
    return render_template('donee/fra_detail.html',fra=fra,comments=comments,is_fav=is_fav)

if __name__=='__main__':
    app.run(debug=True,port=5000)
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
