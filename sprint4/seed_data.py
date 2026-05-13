'''Sprint 4 seed — full dataset including reports.'''
import sys,os,random
from datetime import datetime,timedelta
sys.path.insert(0,os.path.dirname(__file__))
from entity.models import init_db,get_db
from werkzeug.security import generate_password_hash

random.seed(42)
FIRST=['Alex','Jordan','Sam','Taylor','Morgan','Casey','Riley','Jamie']
LAST=['Tan','Lee','Wong','Lim','Chen','Ng','Goh','Chua']
TITLES=['Help Build a Community Library','Clean Water for Pulau Ubin','Youth Coding Camp',
        'Marine Plastic Cleanup','After-School Tutoring','Rescue Dogs Medical Fund',
        'Solar Panels for Community','Mental Health Awareness','Food Bank Drive','Urban Farming']
DESC='We want to make a real difference in our community. Every dollar raised goes directly to the cause. Join us in building something meaningful for future generations.'
REPORT_REASONS=['Images appear to be stock photos, not actual beneficiaries of the cause.',
                'No updates posted in over 90 days despite claiming urgent need.',
                'Goal amount seems disproportionately large for stated activities.']
IMAGE_URLS=[
    'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=600',
    'https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=600',
    'https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=600',
    'https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=600',
    'https://images.unsplash.com/photo-1542810634-71277d95dcbb?w=600',
]

def rand_date(days=300):
    return (datetime.now()-timedelta(days=random.randint(1,days))).isoformat()

def seed():
    print('Initialising Sprint 4 database...')
    init_db()
    conn=get_db(); fr_ids=[]; donee_ids=[]
    for i in range(1,51):
        name=f'{random.choice(FIRST)} {random.choice(LAST)}'
        for role,lst in [('fundraiser',fr_ids),('donee',donee_ids)]:
            email=f'{role}{i}@sprint4.test'
            try:
                conn.execute('INSERT INTO users (full_name,email,password,role,created_at) VALUES (?,?,?,?,?)',
                    (name,email,generate_password_hash('Test1234!'),role,rand_date()))
                row=conn.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()
                lst.append(row['id'])
            except: pass
    cats=[r['id'] for r in conn.execute('SELECT id FROM categories').fetchall()]
    fra_ids=[]
    for i in range(100):
        fr=random.choice(fr_ids) if fr_ids else 1
        st=random.choice(['active']*50+['closed']*20+['draft']*15+['pending_approval']*15)
        now=rand_date(); goal=random.choice([500,1000,2000,5000])
        img=random.choice(IMAGE_URLS)
        conn.execute('INSERT INTO fras (title,description,category_id,monetary_goal,status,created_by,image_url,view_count,favorite_count,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (TITLES[i%len(TITLES)],DESC,random.choice(cats),goal,st,fr,img,random.randint(0,500),random.randint(0,50),now,now))
        fra_ids.append(conn.execute('SELECT last_insert_rowid()').fetchone()[0])
    active_fras=[r['id'] for r in conn.execute("SELECT id FROM fras WHERE status='active'").fetchall()]
    for _ in range(300):
        if not active_fras or not donee_ids: break
        conn.execute('INSERT INTO donations (donor_id,fra_id,amount,message,donated_at) VALUES (?,?,?,?,?)',
            (random.choice(donee_ids),random.choice(active_fras),random.choice([10,25,50,100]),'',rand_date(200)))
    fav_pairs=set()
    for _ in range(200):
        if not active_fras or not donee_ids: break
        u=random.choice(donee_ids); f=random.choice(active_fras)
        if (u,f) not in fav_pairs:
            fav_pairs.add((u,f))
            try: conn.execute('INSERT INTO fra_favorites (user_id,fra_id) VALUES (?,?)',(u,f))
            except: pass
    for _ in range(150):
        if not active_fras or not donee_ids: break
        conn.execute('INSERT INTO comments (fra_id,user_id,content) VALUES (?,?,?)',
            (random.choice(active_fras),random.choice(donee_ids),'Great initiative!'))
    report_pairs=set()
    for _ in range(30):
        if not active_fras or not donee_ids: break
        u=random.choice(donee_ids); f=random.choice(active_fras)
        if (f,u) not in report_pairs:
            report_pairs.add((f,u))
            try:
                conn.execute('INSERT INTO fra_reports (fra_id,reporter_id,reason,status) VALUES (?,?,?,?)',
                    (f,u,random.choice(REPORT_REASONS),random.choice(['pending','reviewed'])))
            except: pass
    # Fixed demo accounts
    fixed_accounts = [
        ('Fundraiser One',  'fundraiser1@tacofundme.test', 'Test1234!', 'fundraiser', 1),
        ('Donee One',       'donee1@tacofundme.test',      'Test1234!', 'donee',      1),
        ('Deactivated User','deactivated@test.com',        'Test1234!', 'donee',      0),
    ]
    for full_name, email, password, role, is_active in fixed_accounts:
        try:
            conn.execute(
                'INSERT INTO users (full_name,email,password,role,is_active,created_at) VALUES (?,?,?,?,?,?)',
                (full_name, email, generate_password_hash(password), role, is_active,
                 datetime.now().isoformat())
            )
        except: pass
    conn.commit(); conn.close()
    print('Sprint 4 seed complete! (Full dataset with reports)')
    print('  Admin:       admin@tacofundme.org / admin123')
    print('  Fundraiser:  fundraiser1@tacofundme.test / Test1234!')
    print('  Donee:       donee1@tacofundme.test / Test1234!')
    print('  Deactivated: deactivated@test.com / Test1234! (inactive)')

if __name__=='__main__':
    seed()
