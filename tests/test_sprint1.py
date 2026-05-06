"""
Sprint 1 Tests — Users & Categories
Covers user stories: #1-9, #11, #23, #35, #36
"""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from entity.models import init_db, get_db
from control.controllers import AuthController, AdminController
from boundary.routes import app


@pytest.fixture(scope='module')
def test_db(tmp_path_factory):
    import entity.models as m
    db = str(tmp_path_factory.mktemp('db') / 'test.db')
    orig = m.DB_PATH; m.DB_PATH = db; init_db()
    yield db; m.DB_PATH = orig


@pytest.fixture(scope='module')
def client(test_db):
    app.config['TESTING'] = True
    with app.test_client() as c:
        c.post('/login', data={'email': 'admin@tacofundme.org', 'password': 'admin123'})
        yield c


# ── Auth Tests (#1, #2) ───────────────────────────────────────────────────────

class TestLogin:
    def test_login_page_loads(self, client):
        r = client.get('/login'); assert r.status_code == 200

    def test_valid_admin_login(self, test_db):
        app.config['TESTING'] = True
        with app.test_client() as c:
            r = c.post('/login', data={'email': 'admin@tacofundme.org', 'password': 'admin123'},
                       follow_redirects=True)
            assert r.status_code == 200

    def test_wrong_password(self, test_db):
        user, err = AuthController.login('admin@tacofundme.org', 'wrongpassword')
        assert user is None; assert 'Incorrect' in err

    def test_unknown_email(self, test_db):
        user, err = AuthController.login('nobody@test.com', 'password')
        assert user is None; assert 'No account' in err

    def test_empty_credentials(self, test_db):
        user, err = AuthController.login('', '')
        assert user is None; assert err


class TestLogout:
    def test_logout_redirects(self, client):
        r = client.get('/logout', follow_redirects=False)
        assert r.status_code in (301, 302)


# ── Registration Tests (#11, #23) ─────────────────────────────────────────────

class TestRegistration:
    def test_register_donee(self, test_db):
        user, err = AuthController.register(
            'Test Donee', 'donee.reg@test.com', 'pass123', 'pass123', 'donee')
        assert user is not None; assert err is None
        assert user['role'] == 'donee'

    def test_register_fundraiser(self, test_db):
        user, err = AuthController.register(
            'Test FR', 'fr.reg@test.com', 'pass123', 'pass123', 'fundraiser')
        assert user is not None; assert user['role'] == 'fundraiser'

    def test_password_mismatch(self, test_db):
        user, err = AuthController.register('X Y', 'x@test.com', 'abc123', 'wrong', 'donee')
        assert user is None; assert 'match' in err

    def test_duplicate_email(self, test_db):
        AuthController.register('A B', 'dup@test.com', 'pass123', 'pass123', 'donee')
        user, err = AuthController.register('C D', 'dup@test.com', 'pass123', 'pass123', 'donee')
        assert user is None; assert 'email' in err.lower()

    def test_short_password(self, test_db):
        user, err = AuthController.register('A B', 'short@test.com', 'ab', 'ab', 'donee')
        assert user is None

    def test_invalid_email(self, test_db):
        user, err = AuthController.register('A B', 'notanemail', 'pass123', 'pass123', 'donee')
        assert user is None


# ── Admin User CRUD Tests (#3-9) ──────────────────────────────────────────────

class TestAdminUserManagement:
    def test_create_user(self, test_db):
        uid, err = AdminController.create_user('New User', 'new@test.com', 'pass123', 'donee')
        assert uid is not None; assert err is None

    def test_create_duplicate_email(self, test_db):
        AdminController.create_user('A', 'uniq@test.com', 'pass123', 'donee')
        uid, err = AdminController.create_user('B', 'uniq@test.com', 'pass123', 'donee')
        assert uid is None

    def test_create_invalid_role(self, test_db):
        uid, err = AdminController.create_user('A', 'r@test.com', 'pass123', 'hacker')
        assert uid is None; assert 'Invalid role' in err

    def test_get_user(self, test_db):
        uid, _ = AdminController.create_user('Get Me', 'getme@test.com', 'pass123', 'donee')
        user, err = AdminController.get_user(uid)
        assert user is not None; assert 'password' not in user

    def test_get_nonexistent_user(self, test_db):
        user, err = AdminController.get_user(99999)
        assert user is None; assert err

    def test_deactivate_user(self, test_db):
        uid, _ = AdminController.create_user('Deact Me', 'deact@test.com', 'pass123', 'donee')
        ok, msg = AdminController.deactivate_user(uid, 1)
        assert ok; user, _ = AdminController.get_user(uid)
        assert user['is_active'] == 0

    def test_reactivate_user(self, test_db):
        uid, _ = AdminController.create_user('React Me', 'react@test.com', 'pass123', 'donee')
        AdminController.deactivate_user(uid, 1)
        ok, msg = AdminController.reactivate_user(uid)
        assert ok

    def test_delete_user(self, test_db):
        uid, _ = AdminController.create_user('Del Me', 'delme@test.com', 'pass123', 'donee')
        ok, msg = AdminController.delete_user(uid, 1)
        assert ok; user, err = AdminController.get_user(uid)
        assert user is None

    def test_cannot_delete_self(self, test_db):
        ok, msg = AdminController.delete_user(1, 1)
        assert not ok

    def test_reset_password(self, test_db):
        uid, _ = AdminController.create_user('Reset Me', 'reset@test.com', 'oldpass', 'donee')
        ok, msg = AdminController.reset_password(uid, 'newpass123', 1)
        assert ok
        user2, err = AuthController.login('reset@test.com', 'newpass123')
        assert user2 is not None

    def test_search_users(self, test_db):
        AdminController.create_user('Searchable User', 'searchable@test.com', 'pass123', 'donee')
        users, total = AdminController.list_users(search='Searchable')
        assert total >= 1; assert any('Searchable' in u['full_name'] for u in users)

    def test_list_page(self, client):
        r = client.get('/admin/users'); assert r.status_code == 200


# ── Category Tests (#35, #36) ─────────────────────────────────────────────────

class TestCategoryManagement:
    def test_create_category(self, test_db):
        cid, err = AdminController.create_category('Sports', 'Sporting activities')
        assert cid is not None; assert err is None

    def test_create_duplicate_category(self, test_db):
        AdminController.create_category('Unique Cat', 'desc')
        cid, err = AdminController.create_category('Unique Cat', 'desc')
        assert cid is None

    def test_create_short_name(self, test_db):
        cid, err = AdminController.create_category('A', '')
        assert cid is None

    def test_edit_category(self, test_db):
        cid, _ = AdminController.create_category('Edit Me', 'old desc')
        ok, msg = AdminController.update_category(cid, 'Edited Name', 'new desc')
        assert ok

    def test_categories_page_loads(self, client):
        r = client.get('/admin/categories'); assert r.status_code == 200
