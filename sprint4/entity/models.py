"""
ENTITY LAYER — BCE Architecture
Pure data access only. No business logic, no HTTP.


"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'tacofundme.db')


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'donee',
            bio        TEXT,
            phone      TEXT,
            address    TEXT,
            is_active  INTEGER NOT NULL DEFAULT 1,
            created_at TEXT    NOT NULL,
            last_login TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fras (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT    NOT NULL,
            description   TEXT    NOT NULL DEFAULT '',
            category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
            monetary_goal REAL    NOT NULL DEFAULT 0,
            view_count    INTEGER NOT NULL DEFAULT 0,
            favorite_count INTEGER NOT NULL DEFAULT 0,
            status        TEXT    NOT NULL DEFAULT 'draft',
            image_url     TEXT,
            created_by    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at    TEXT    NOT NULL,
            updated_at    TEXT    NOT NULL
        )
    """)

    try:
        cur.execute("ALTER TABLE fras ADD COLUMN image_url TEXT")
    except Exception:
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            fra_id     INTEGER NOT NULL REFERENCES fras(id) ON DELETE CASCADE,
            amount     REAL    NOT NULL,
            message    TEXT    NOT NULL DEFAULT '',
            donated_at TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fra_favorites (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            fra_id  INTEGER NOT NULL REFERENCES fras(id) ON DELETE CASCADE,
            UNIQUE(user_id, fra_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fra_id     INTEGER NOT NULL REFERENCES fras(id) ON DELETE CASCADE,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            content    TEXT    NOT NULL,
            parent_id  INTEGER REFERENCES comments(id) ON DELETE CASCADE,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fra_reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fra_id      INTEGER NOT NULL REFERENCES fras(id) ON DELETE CASCADE,
            reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reason      TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'pending',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE(fra_id, reporter_id)
        )
    """)

    default_cats = [
        ('Education',       'Learning and scholarship initiatives'),
        ('Health',          'Medical aid and wellness programmes'),
        ('Environment',     'Conservation and sustainability efforts'),
        ('Community',       'Neighbourhood and social welfare projects'),
        ('Arts & Culture',  'Creative and cultural preservation'),
        ('Disaster Relief', 'Emergency response and recovery'),
        ('Animals',         'Animal welfare and rescue organizations'),
        ('Technology',      'Tech education and digital inclusion'),
    ]
    for name, desc in default_cats:
        cur.execute("SELECT id FROM categories WHERE name=?", (name,))
        if not cur.fetchone():
            cur.execute("INSERT INTO categories (name, description) VALUES (?,?)", (name, desc))

    # init_db is bootstrap code — hashing here is acceptable
    cur.execute("SELECT id, password FROM users WHERE email='admin@tacofundme.org'")
    row = cur.fetchone()
    hashed_pw = generate_password_hash('admin123')
    if row:
        pw = row['password']
        if not (pw.startswith('pbkdf2:') or pw.startswith('scrypt:')):
            cur.execute("UPDATE users SET password=? WHERE id=?", (hashed_pw, row['id']))
    else:
        cur.execute("""
            INSERT INTO users (full_name, email, password, role, bio, created_at)
            VALUES (?,?,?,?,?,?)
        """, ('Admin User', 'admin@tacofundme.org', hashed_pw, 'admin',
              'Platform administrator.', datetime.now().isoformat()))

    conn.commit()
    conn.close()


# ── BaseEntity ────────────────────────────────────────────────────────────────

class BaseEntity:
    """
    Shared database helpers for all entity classes.
    Using @classmethod (not @staticmethod) so subclasses can override _db()
    and the class itself is a proper participant in the inheritance hierarchy.
    """

    @classmethod
    def _db(cls):
        return get_db()

    @classmethod
    def _fetchone(cls, sql: str, params: tuple = ()):
        conn = cls._db()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return dict(row) if row else None

    @classmethod
    def _fetchall(cls, sql: str, params: tuple = ()):
        conn = cls._db()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def _execute(cls, sql: str, params: tuple = ()):
        """Execute a write statement; returns lastrowid."""
        conn = cls._db()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


# ── UserEntity ────────────────────────────────────────────────────────────────

class UserEntity(BaseEntity):

    @classmethod
    def find_by_email(cls, email: str):
        return cls._fetchone("SELECT * FROM users WHERE email=?", (email,))

    @classmethod
    def find_by_id(cls, user_id: int):
        return cls._fetchone("SELECT * FROM users WHERE id=?", (user_id,))

    @classmethod
    def create(cls, full_name: str, email: str, hashed_password: str, role: str = 'donee'):
        """
        Accepts an already-hashed password.
        Hashing is the Control layer's responsibility (encapsulation fix).
        """
        conn = cls._db()
        try:
            cur = conn.execute("""
                INSERT INTO users (full_name, email, password, role, created_at)
                VALUES (?,?,?,?,?)
            """, (full_name, email, hashed_password, role, datetime.now().isoformat()))
            conn.commit()
            uid = cur.lastrowid
            conn.close()
            return uid, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "An account with this email already exists"

    @classmethod
    def update(cls, user_id: int, **kwargs):
        allowed = {'full_name', 'email', 'bio', 'phone', 'address', 'role', 'is_active'}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return True, None
        clause = ', '.join(f"{k}=?" for k in fields)
        conn = cls._db()
        try:
            conn.execute(f"UPDATE users SET {clause} WHERE id=?", list(fields.values()) + [user_id])
            conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            conn.rollback()
            return False, "An account with this email already exists"
        finally:
            conn.close()

    @classmethod
    def update_password(cls, user_id: int, hashed_password: str):
        """Accepts an already-hashed password (hashing done in Control layer)."""
        cls._execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))

    @classmethod
    def record_login(cls, user_id: int):
        cls._execute("UPDATE users SET last_login=? WHERE id=?",
                     (datetime.now().isoformat(), user_id))

    @classmethod
    def delete(cls, user_id: int):
        cls._execute("DELETE FROM users WHERE id=?", (user_id,))

    @classmethod
    def search(cls, query: str = '', role: str = None, is_active=None,
               page: int = 1, per_page: int = 20):
        conn = cls._db()
        where, params = [], []
        if query:
            where.append("(full_name LIKE ? OR email LIKE ?)")
            params += [f'%{query}%', f'%{query}%']
        if role:
            where.append("role=?"); params.append(role)
        if is_active is not None:
            where.append("is_active=?"); params.append(1 if is_active else 0)
        w = ("WHERE " + " AND ".join(where)) if where else ""
        total = conn.execute(f"SELECT COUNT(*) FROM users {w}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM users {w} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page]
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows], total

    @classmethod
    def count_by_role(cls):
        rows = cls._fetchall("SELECT role, COUNT(*) as cnt FROM users GROUP BY role")
        return {r['role']: r['cnt'] for r in rows}

    @classmethod
    def count_new(cls, days: int = 30):
        conn = cls._db()
        n = conn.execute(
            "SELECT COUNT(*) FROM users WHERE created_at >= datetime('now',?)",
            (f'-{days} days',)
        ).fetchone()[0]
        conn.close()
        return n


# ── CategoryEntity ────────────────────────────────────────────────────────────

class CategoryEntity(BaseEntity):

    @classmethod
    def get_all(cls):
        return cls._fetchall("SELECT * FROM categories ORDER BY name")

    @classmethod
    def find_by_id(cls, cat_id: int):
        return cls._fetchone("SELECT * FROM categories WHERE id=?", (cat_id,))

    @classmethod
    def find_by_name(cls, name: str):
        return cls._fetchone("SELECT * FROM categories WHERE name=?", (name,))

    @classmethod
    def search(cls, query: str = ''):
        if query:
            return cls._fetchall(
                "SELECT * FROM categories WHERE name LIKE ? OR description LIKE ? ORDER BY name",
                (f'%{query}%', f'%{query}%')
            )
        return cls._fetchall("SELECT * FROM categories ORDER BY name")

    @classmethod
    def create(cls, name: str, description: str = ''):
        conn = cls._db()
        try:
            cur = conn.execute(
                "INSERT INTO categories (name, description) VALUES (?,?)", (name, description)
            )
            conn.commit()
            cid = cur.lastrowid
            conn.close()
            return cid, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "A category with this name already exists"

    @classmethod
    def update(cls, cat_id: int, name: str = None, description: str = None):
        conn = cls._db()
        try:
            if name is not None:
                conn.execute("UPDATE categories SET name=? WHERE id=?", (name, cat_id))
            if description is not None:
                conn.execute("UPDATE categories SET description=? WHERE id=?", (description, cat_id))
            conn.commit()
            conn.close()
            return True, None
        except sqlite3.IntegrityError:
            conn.close()
            return False, "A category with this name already exists"

    @classmethod
    def delete(cls, cat_id: int):
        cls._execute("DELETE FROM categories WHERE id=?", (cat_id,))


# ── FRAEntity ─────────────────────────────────────────────────────────────────

class FRAEntity(BaseEntity):

    @classmethod
    def create(cls, title, description, category_id, monetary_goal, created_by, image_url=None):
        conn = cls._db()
        now = datetime.now().isoformat()
        cur = conn.execute("""
            INSERT INTO fras (title,description,category_id,monetary_goal,created_by,
                              image_url,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (title, description, category_id, monetary_goal, created_by, image_url, now, now))
        conn.commit()
        fra_id = cur.lastrowid
        conn.close()
        return fra_id

    @classmethod
    def find_by_id(cls, fra_id: int):
        return cls._fetchone("""
            SELECT f.*,
                   c.name as category_name,
                   u.full_name as fundraiser_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised,
                   (SELECT COUNT(*) FROM fra_reports WHERE fra_id=f.id AND status='pending') as report_count
            FROM fras f
            LEFT JOIN categories c ON f.category_id=c.id
            LEFT JOIN users u ON f.created_by=u.id
            WHERE f.id=?
        """, (fra_id,))

    @classmethod
    def find_by_owner(cls, user_id: int, search: str = '', category_id=None,
                      status: str = None, start_date: str = None, end_date: str = None):
        conn = cls._db()
        where = ["f.created_by=?"]
        params = [user_id]
        if search:
            where.append("(f.title LIKE ? OR f.description LIKE ?)")
            params += [f'%{search}%', f'%{search}%']
        if category_id:
            where.append("f.category_id=?"); params.append(int(category_id))
        if status:
            where.append("f.status=?"); params.append(status)
        if start_date:
            where.append("f.created_at>=?"); params.append(start_date)
        if end_date:
            where.append("f.created_at<=?"); params.append(end_date + 'T23:59:59')
        w = "WHERE " + " AND ".join(where)
        rows = conn.execute(f"""
            SELECT f.*, c.name as category_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised
            FROM fras f
            LEFT JOIN categories c ON f.category_id=c.id
            {w} ORDER BY f.created_at DESC
        """, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_all_active(cls, search: str = '', category_id=None, page: int = 1, per_page: int = 12):
        conn = cls._db()
        where = ["f.status='active'"]
        params = []
        if search:
            where.append("(f.title LIKE ? OR f.description LIKE ?)")
            params += [f'%{search}%', f'%{search}%']
        if category_id:
            where.append("f.category_id=?"); params.append(int(category_id))
        w = "WHERE " + " AND ".join(where)
        total = conn.execute(f"SELECT COUNT(*) FROM fras f {w}", params).fetchone()[0]
        rows = conn.execute(f"""
            SELECT f.*, c.name as category_name, u.full_name as fundraiser_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised
            FROM fras f
            LEFT JOIN categories c ON f.category_id=c.id
            LEFT JOIN users u ON f.created_by=u.id
            {w} ORDER BY f.created_at DESC LIMIT ? OFFSET ?
        """, params + [per_page, (page - 1) * per_page]).fetchall()
        conn.close()
        return [dict(r) for r in rows], total

    @classmethod
    def get_all(cls, search: str = '', status: str = None, category_id=None,
                page: int = 1, per_page: int = 20):
        conn = cls._db()
        where, params = [], []
        if search:
            where.append("(f.title LIKE ? OR f.description LIKE ?)")
            params += [f'%{search}%', f'%{search}%']
        if status:
            where.append("f.status=?"); params.append(status)
        if category_id:
            where.append("f.category_id=?"); params.append(int(category_id))
        w = ("WHERE " + " AND ".join(where)) if where else ""
        total = conn.execute(f"SELECT COUNT(*) FROM fras f {w}", params).fetchone()[0]
        rows = conn.execute(f"""
            SELECT f.*, c.name as category_name, u.full_name as fundraiser_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised,
                   (SELECT COUNT(*) FROM fra_reports WHERE fra_id=f.id AND status='pending') as report_count
            FROM fras f
            LEFT JOIN categories c ON f.category_id=c.id
            LEFT JOIN users u ON f.created_by=u.id
            {w} ORDER BY f.created_at DESC LIMIT ? OFFSET ?
        """, params + [per_page, (page - 1) * per_page]).fetchall()
        conn.close()
        return [dict(r) for r in rows], total

    @classmethod
    def get_pending_approval(cls):
        return cls._fetchall("""
            SELECT f.*, c.name as category_name, u.full_name as fundraiser_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised
            FROM fras f
            LEFT JOIN categories c ON f.category_id=c.id
            LEFT JOIN users u ON f.created_by=u.id
            WHERE f.status='pending_approval'
            ORDER BY f.updated_at ASC
        """)

    @classmethod
    def get_favorites_for_user(cls, user_id: int):
        return cls._fetchall("""
            SELECT f.*, c.name as category_name, u.full_name as fundraiser_name,
                   COALESCE((SELECT SUM(amount) FROM donations WHERE fra_id=f.id),0) as amount_raised,
                   ff.rowid as fav_id
            FROM fra_favorites ff
            JOIN fras f ON ff.fra_id=f.id
            LEFT JOIN categories c ON f.category_id=c.id
            LEFT JOIN users u ON f.created_by=u.id
            WHERE ff.user_id=?
            ORDER BY ff.id DESC
        """, (user_id,))

    @classmethod
    def update_fields(cls, fra_id: int, **kwargs):
        allowed = {'title', 'description', 'category_id', 'monetary_goal',
                   'status', 'image_url', 'view_count', 'favorite_count'}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return
        fields['updated_at'] = datetime.now().isoformat()
        clause = ', '.join(f"{k}=?" for k in fields)
        conn = cls._db()
        conn.execute(f"UPDATE fras SET {clause} WHERE id=?", list(fields.values()) + [fra_id])
        conn.commit()
        conn.close()

    @classmethod
    def delete(cls, fra_id: int):
        cls._execute("DELETE FROM fras WHERE id=?", (fra_id,))

    @classmethod
    def increment_views(cls, fra_id: int):
        cls._execute("UPDATE fras SET view_count=view_count+1 WHERE id=?", (fra_id,))

    @classmethod
    def platform_stats(cls):
        return cls._fetchone("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) as active,
                   SUM(CASE WHEN status='pending_approval' THEN 1 ELSE 0 END) as pending,
                   SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed,
                   SUM(CASE WHEN status='draft' THEN 1 ELSE 0 END) as draft
            FROM fras
        """) or {}

    @classmethod
    def owner_stats(cls, user_id: int):
        return cls._fetchone("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) as active,
                   SUM(CASE WHEN status='draft' THEN 1 ELSE 0 END) as draft,
                   SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed,
                   SUM(view_count) as total_views,
                   SUM(favorite_count) as total_favorites,
                   COALESCE((SELECT SUM(d.amount) FROM donations d
                              JOIN fras f2 ON d.fra_id=f2.id WHERE f2.created_by=?),0) as total_raised
            FROM fras WHERE created_by=?
        """, (user_id, user_id)) or {}


# ── DonationEntity ────────────────────────────────────────────────────────────

class DonationEntity(BaseEntity):

    @classmethod
    def create(cls, donor_id: int, fra_id: int, amount: float, message: str) -> int:
        return cls._execute("""
            INSERT INTO donations (donor_id,fra_id,amount,message,donated_at)
            VALUES (?,?,?,?,?)
        """, (donor_id, fra_id, amount, message, datetime.now().isoformat()))

    @classmethod
    def find_by_donor(cls, donor_id: int, category_id=None,
                      start_date: str = None, end_date: str = None):
        conn = cls._db()
        where = ["d.donor_id=?"]
        params = [donor_id]
        if category_id:
            where.append("f.category_id=?"); params.append(int(category_id))
        if start_date:
            where.append("d.donated_at>=?"); params.append(start_date)
        if end_date:
            where.append("d.donated_at<=?"); params.append(end_date + 'T23:59:59')
        w = "WHERE " + " AND ".join(where)
        rows = conn.execute(f"""
            SELECT d.*, f.title as fra_title, f.status as fra_status,
                   c.name as category_name
            FROM donations d
            JOIN fras f ON d.fra_id=f.id
            LEFT JOIN categories c ON f.category_id=c.id
            {w} ORDER BY d.donated_at DESC
        """, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def find_by_fra(cls, fra_id: int):
        return cls._fetchall("""
            SELECT d.*, u.full_name as donor_name
            FROM donations d JOIN users u ON d.donor_id=u.id
            WHERE d.fra_id=? ORDER BY d.donated_at DESC
        """, (fra_id,))

    @classmethod
    def platform_total(cls) -> float:
        conn = cls._db()
        val = conn.execute("SELECT COALESCE(SUM(amount),0) FROM donations").fetchone()[0]
        conn.close()
        return float(val)

    @classmethod
    def count_all(cls) -> int:
        conn = cls._db()
        n = conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0]
        conn.close()
        return n

    @classmethod
    def period_breakdown(cls, period: str = 'monthly'):
        conn = cls._db()
        if period == 'daily':
            fmt, interval = "%Y-%m-%d", '-30 days'
        elif period == 'weekly':
            fmt, interval = "%Y-W%W", '-84 days'
        else:
            fmt, interval = "%Y-%m", '-365 days'
        rows = conn.execute(f"""
            SELECT strftime('{fmt}', donated_at) as period,
                   SUM(amount) as total_amount,
                   COUNT(*) as donation_count
            FROM donations
            WHERE donated_at >= datetime('now','{interval}')
            GROUP BY period ORDER BY period DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ── FRAFavoriteEntity ─────────────────────────────────────────────────────────

class FRAFavoriteEntity(BaseEntity):

    @classmethod
    def toggle(cls, user_id: int, fra_id: int) -> bool:
        conn = cls._db()
        row = conn.execute(
            "SELECT id FROM fra_favorites WHERE user_id=? AND fra_id=?", (user_id, fra_id)
        ).fetchone()
        if row:
            conn.execute("DELETE FROM fra_favorites WHERE user_id=? AND fra_id=?", (user_id, fra_id))
            conn.execute("UPDATE fras SET favorite_count=MAX(0,favorite_count-1) WHERE id=?", (fra_id,))
            conn.commit(); conn.close()
            return False
        conn.execute("INSERT INTO fra_favorites (user_id,fra_id) VALUES (?,?)", (user_id, fra_id))
        conn.execute("UPDATE fras SET favorite_count=favorite_count+1 WHERE id=?", (fra_id,))
        conn.commit(); conn.close()
        return True

    @classmethod
    def is_favorited(cls, user_id: int, fra_id: int) -> bool:
        row = cls._fetchone(
            "SELECT id FROM fra_favorites WHERE user_id=? AND fra_id=?", (user_id, fra_id)
        )
        return row is not None


# ── CommentEntity ─────────────────────────────────────────────────────────────

class CommentEntity(BaseEntity):

    @classmethod
    def create(cls, fra_id: int, user_id: int, content: str, parent_id=None) -> int:
        return cls._execute("""
            INSERT INTO comments (fra_id, user_id, content, parent_id)
            VALUES (?,?,?,?)
        """, (fra_id, user_id, content, parent_id))

    @classmethod
    def find_by_id(cls, comment_id: int):
        return cls._fetchone("SELECT * FROM comments WHERE id=?", (comment_id,))

    @classmethod
    def list_for_fra(cls, fra_id: int):
        conn = cls._db()
        top = conn.execute("""
            SELECT c.*, u.full_name as user_name, u.role as user_role
            FROM comments c JOIN users u ON c.user_id=u.id
            WHERE c.fra_id=? AND c.parent_id IS NULL
            ORDER BY c.created_at ASC
        """, (fra_id,)).fetchall()
        result = []
        for row in top:
            d = dict(row)
            replies = conn.execute("""
                SELECT c.*, u.full_name as user_name, u.role as user_role
                FROM comments c JOIN users u ON c.user_id=u.id
                WHERE c.parent_id=? ORDER BY c.created_at ASC
            """, (d['id'],)).fetchall()
            d['replies'] = [dict(r) for r in replies]
            result.append(d)
        conn.close()
        return result


# ── ReportEntity ──────────────────────────────────────────────────────────────

class ReportEntity(BaseEntity):

    @classmethod
    def create(cls, fra_id: int, reporter_id: int, reason: str):
        conn = cls._db()
        try:
            cur = conn.execute("""
                INSERT INTO fra_reports (fra_id, reporter_id, reason)
                VALUES (?,?,?)
            """, (fra_id, reporter_id, reason))
            conn.commit()
            rid = cur.lastrowid
            conn.close()
            return rid, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "You have already reported this fundraising activity"

    @classmethod
    def list_all(cls, keyword: str = None, status: str = None,
                 start_date: str = None, end_date: str = None):
        conn = cls._db()
        where, params = [], []
        if keyword:
            where.append("(f.title LIKE ? OR u.full_name LIKE ? OR r.reason LIKE ?)")
            params += [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
        if status:
            where.append("r.status=?"); params.append(status)
        if start_date:
            where.append("r.created_at>=?"); params.append(start_date)
        if end_date:
            where.append("r.created_at<=?"); params.append(end_date + 'T23:59:59')
        w = ("WHERE " + " AND ".join(where)) if where else ""
        rows = conn.execute(f"""
            SELECT r.*, f.title as fra_title, u.full_name as reporter_name
            FROM fra_reports r
            JOIN fras f ON r.fra_id=f.id
            JOIN users u ON r.reporter_id=u.id
            {w} ORDER BY r.created_at DESC
        """, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def update_status(cls, report_id: int, status: str):
        cls._execute("UPDATE fra_reports SET status=? WHERE id=?", (status, report_id))
