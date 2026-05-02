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

def admin_required(f):
    @wraps(f)
    @login_required
    def d(*a,**kw):
        if session.get('role')!='admin':
            flash('Admin access required.','danger'); return redirect(url_for('dashboard'))
        return f(*a,**kw)
    return d

def fundraiser_required(f):
    @wraps(f)
    @login_required
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

@app.route('/dashboard')
@login_required
def dashboard():
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

@app.route('/admin/users')
@admin_required
def admin_users():
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

@app.route('/admin/categories')
@admin_required
def admin_categories():
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

@app.route('/admin/fras')
@admin_required
def admin_fras():
    s=request.args.get('q',''); st=request.args.get('status',''); ci=request.args.get('category_id','')
    page=max(1,request.args.get('page',1,type=int))
    fras,total=AdminController.list_fras(s,st or None,int(ci) if ci else None,page)
    return render_template('admin/fras.html',fras=fras,total=total,pages=max(1,(total+19)//20),
        search=s,status=st,cat_id=ci,categories=CategoryController.list_all(),page=page)

@app.route('/admin/fras/approvals')
@admin_required
def admin_approvals():
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

@app.route('/fundraiser/fras')
@fundraiser_required
def fr_fras():
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

@app.route('/browse')
@login_required
def browse():
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
