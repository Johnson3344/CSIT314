<<<<<<< HEAD
'''Sprint 4 seed — full dataset including reports.'''
=======
<<<<<<< HEAD
'''Sprint 3 seed — users, FRAs, donations, favourites, comments.'''
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
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
<<<<<<< HEAD
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
=======
MSGS=['Keep up the great work!','Happy to support this amazing cause.','',
      'This really matters, thank you.','Wishing you all the best!','']
CMTS=['This is such an important cause!','How can I volunteer?','Shared with my team!',
      'Will there be updates on progress?','Donated with pleasure!']
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c

def rand_date(days=300):
    return (datetime.now()-timedelta(days=random.randint(1,days))).isoformat()

def seed():
<<<<<<< HEAD
    print('Initialising Sprint 4 database...')
=======
    print('Initialising Sprint 3 database...')
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    init_db()
    conn=get_db(); fr_ids=[]; donee_ids=[]
    for i in range(1,51):
        name=f'{random.choice(FIRST)} {random.choice(LAST)}'
        for role,lst in [('fundraiser',fr_ids),('donee',donee_ids)]:
<<<<<<< HEAD
            email=f'{role}{i}@sprint4.test'
=======
            email=f'{role}{i}@sprint3.test'
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
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
<<<<<<< HEAD
        img=random.choice(IMAGE_URLS)
        conn.execute('INSERT INTO fras (title,description,category_id,monetary_goal,status,created_by,image_url,view_count,favorite_count,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (TITLES[i%len(TITLES)],DESC,random.choice(cats),goal,st,fr,img,random.randint(0,500),random.randint(0,50),now,now))
=======
        conn.execute('INSERT INTO fras (title,description,category_id,monetary_goal,status,created_by,view_count,favorite_count,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
            (TITLES[i%len(TITLES)],DESC,random.choice(cats),goal,st,fr,random.randint(0,500),random.randint(0,50),now,now))
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
        fra_ids.append(conn.execute('SELECT last_insert_rowid()').fetchone()[0])
    active_fras=[r['id'] for r in conn.execute("SELECT id FROM fras WHERE status='active'").fetchall()]
    for _ in range(300):
        if not active_fras or not donee_ids: break
        conn.execute('INSERT INTO donations (donor_id,fra_id,amount,message,donated_at) VALUES (?,?,?,?,?)',
<<<<<<< HEAD
            (random.choice(donee_ids),random.choice(active_fras),random.choice([10,25,50,100]),'',rand_date(200)))
=======
            (random.choice(donee_ids),random.choice(active_fras),
             random.choice([10,25,50,100,200]),random.choice(MSGS),rand_date(200)))
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
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
<<<<<<< HEAD
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
        ('Fundraiser One', 'fundraiser1@tacofundme.test', 'Test1234!', 'fundraiser', 1),
        ('Donee One',      'donee1@tacofundme.test',      'Test1234!', 'donee',      1),
        ('Deactivated User','deactivated@test.com',       'Test1234!', 'donee',      0),
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
=======
            (random.choice(active_fras),random.choice(donee_ids),random.choice(CMTS)))
    conn.commit(); conn.close()
    print('Sprint 3 seed complete!')
    print('  Admin:      admin@tacofundme.org / admin123')
    print('  Fundraiser: fundraiser1@sprint3.test / Test1234!')
    print('  Donee:      donee1@sprint3.test / Test1234!')

if __name__=='__main__':
=======
'''Sprint 2 seed — users, categories, and FRAs.'''
import sys, os, random
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from entity.models import init_db, get_db
from werkzeug.security import generate_password_hash

random.seed(42)
FIRST = ['Alex','Jordan','Sam','Taylor','Morgan','Casey','Riley','Jamie']
LAST  = ['Tan','Lee','Wong','Lim','Chen','Ng','Goh','Chua']
TITLES = [
    'Help Build a Community Library','Clean Water for Pulau Ubin',
    'Youth Coding Camp Scholarships','Marine Plastic Cleanup',
    'After-School Tutoring Programme','Rescue Dogs Medical Fund',
    'Solar Panels for Community Centre','Mental Health Awareness',
    'Food Bank Expansion Drive','Urban Beekeeping Education',
    'Digital Library for Seniors','Free Eye Tests for School Children',
]
DESCS = [
    'We want to make a real difference in our community. Every dollar raised goes directly to the cause. Join us in building something meaningful for future generations.',
    'Your support will help us achieve our goal and create lasting change. We have a dedicated team ready to put donations to work immediately.',
]

def rand_date(days=300):
    d = datetime.now() - timedelta(days=random.randint(1, days))
    return d.isoformat()

def seed():
    print('Initialising Sprint 2 database...')
    init_db()
    conn = get_db()
    fr_ids, donee_ids = [], []

    for i in range(1, 51):
        name = f'{random.choice(FIRST)} {random.choice(LAST)}'
        for role, lst in [('fundraiser', fr_ids), ('donee', donee_ids)]:
            email = f'{role}{i}@sprint2.test'
            try:
                conn.execute('INSERT INTO users (full_name,email,password,role,created_at) VALUES (?,?,?,?,?)',
                    (name, email, generate_password_hash('Test1234!'), role, rand_date()))
                row = conn.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
                lst.append(row['id'])
            except Exception:
                pass

    cats = [r['id'] for r in conn.execute('SELECT id FROM categories').fetchall()]
    statuses = ['active']*50 + ['closed']*20 + ['draft']*15 + ['pending_approval']*15
    random.shuffle(statuses)

    for i, status in enumerate(statuses[:100]):
        title = TITLES[i % len(TITLES)]
        fr_id = random.choice(fr_ids) if fr_ids else 1
        goal = random.choice([500,1000,2000,5000,10000])
        now = rand_date()
        conn.execute('INSERT INTO fras (title,description,category_id,monetary_goal,status,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)',
            (title, random.choice(DESCS), random.choice(cats), goal, status, fr_id, now, now))

    conn.commit(); conn.close()
    print('Sprint 2 seed complete!')
    print('  Admin:      admin@tacofundme.org / admin123')
    print('  Fundraiser: fundraiser1@sprint2.test / Test1234!')
    print('  Donee:      donee1@sprint2.test / Test1234!')

if __name__ == '__main__':
>>>>>>> 524c812935e1415245bb42074faf40f44b69adb1
>>>>>>> 9478613c98caa37fe00de88251adc6915e95526c
    seed()
