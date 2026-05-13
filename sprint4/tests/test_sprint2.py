'''Sprint 2 Tests — FRA management.'''
import pytest,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
from entity.models import init_db
from control.controllers import FundraiserController,AdminController,AuthController
from boundary.routes import app

@pytest.fixture(scope='module')
def test_db(tmp_path_factory):
    import entity.models as m
    db=str(tmp_path_factory.mktemp('db')/'test.db'); orig=m.DB_PATH
    m.DB_PATH=db; init_db(); yield db; m.DB_PATH=orig

@pytest.fixture(scope='module')
def client(test_db):
    app.config['TESTING']=True
    with app.test_client() as c:
        c.post('/login',data={'email':'admin@tacofundme.org','password':'admin123'})
        yield c

@pytest.fixture(scope='module')
def fr_client(test_db):
    app.config['TESTING']=True
    AuthController.register('FR Test','fr@sprint2.test','pass123','pass123','fundraiser')
    with app.test_client() as c:
        c.post('/login',data={'email':'fr@sprint2.test','password':'pass123'})
        yield c

class TestFRACreation:
    def test_create_fra(self,test_db):
        AuthController.register('FR','fra_test@test.com','pass123','pass123','fundraiser')
        from entity.models import UserEntity
        uid=UserEntity.find_by_email('fra_test@test.com')['id']
        fid,err=FundraiserController.create_fra(uid,'My Test Campaign','A long enough description here.',None,1000)
        assert fid; assert err is None

    def test_short_title(self,test_db):
        fid,err=FundraiserController.create_fra(1,'AB','Valid description here.',None,1000)
        assert fid is None

    def test_negative_goal(self,test_db):
        fid,err=FundraiserController.create_fra(1,'Valid Title','Valid description here.',None,-100)
        assert fid is None

    def test_create_fra_page(self,fr_client):
        r=fr_client.get('/fundraiser/fras/create'); assert r.status_code==200

class TestFRAApproval:
    def test_approve_pending_fra(self,test_db):
        from entity.models import FRAEntity,UserEntity
        AuthController.register('FR2','fr2@test.com','pass123','pass123','fundraiser')
        uid=UserEntity.find_by_email('fr2@test.com')['id']
        fid=FRAEntity.create('Pending FRA','Long enough description here.',None,500,uid)
        FRAEntity.update_fields(fid,status='pending_approval')
        ok,msg=AdminController.approve_fra(fid); assert ok
        fra=FRAEntity.find_by_id(fid); assert fra['status']=='active'

    def test_reject_pending_fra(self,test_db):
        from entity.models import FRAEntity,UserEntity
        uid=UserEntity.find_by_email('fr2@test.com')['id']
        fid=FRAEntity.create('Reject Me FRA','Long enough description.',None,500,uid)
        FRAEntity.update_fields(fid,status='pending_approval')
        ok,msg=AdminController.reject_fra(fid); assert ok
        fra=FRAEntity.find_by_id(fid); assert fra['status']=='draft'

    def test_approvals_page(self,client):
        r=client.get('/admin/fras/approvals'); assert r.status_code==200

class TestCategoryDelete:
    def test_delete_category(self,test_db):
        cid,_=AdminController.create_category('ToDelete','test')
        ok,msg=AdminController.delete_category(cid); assert ok
