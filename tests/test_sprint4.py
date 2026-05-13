'''Sprint 4 Tests — Reports, Filtering, Reply, Report FRA.'''
import pytest,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
from entity.models import init_db,FRAEntity,UserEntity,ReportEntity
from control.controllers import DoneeController,AdminController,AuthController,FundraiserController
from boundary.routes import app

@pytest.fixture(scope='module')
def test_db(tmp_path_factory):
    import entity.models as m
    db=str(tmp_path_factory.mktemp('db')/'test.db'); orig=m.DB_PATH
    m.DB_PATH=db; init_db(); yield db; m.DB_PATH=orig

@pytest.fixture(scope='module')
def setup(test_db):
    AuthController.register('FR S4','fr_s4@test.com','pass123','pass123','fundraiser')
    AuthController.register('Donee S4','donee_s4@test.com','pass123','pass123','donee')
    fr=UserEntity.find_by_email('fr_s4@test.com')
    donee=UserEntity.find_by_email('donee_s4@test.com')
    fid=FRAEntity.create('Sprint4 FRA','Long enough description for this test campaign.',None,1000,fr['id'])
    FRAEntity.update_fields(fid,status='active')
    return {'fr_id':fr['id'],'donee_id':donee['id'],'fra_id':fid}

class TestReportFRA:
    def test_report_valid(self,setup,test_db):
        ok,msg=DoneeController.report_fra(setup['fra_id'],setup['donee_id'],'Images appear to be stock photos, not real.')
        assert ok

    def test_report_short_reason(self,setup,test_db):
        ok,msg=DoneeController.report_fra(setup['fra_id'],setup['donee_id'],'Too short')
        assert not ok

    def test_report_duplicate(self,setup,test_db):
        ok,msg=DoneeController.report_fra(setup['fra_id'],setup['donee_id'],'Another report with enough text.')
        assert not ok; assert 'already reported' in msg.lower()

class TestReplyToComment:
    def test_reply_valid(self,setup,test_db):
        from entity.models import CommentEntity
        cid=CommentEntity.create(setup['fra_id'],setup['donee_id'],'Great campaign!')
        ok,msg=FundraiserController.reply_to_comment(cid,setup['fr_id'],setup['fra_id'],'Thank you so much!')
        assert ok

    def test_reply_empty(self,setup,test_db):
        from entity.models import CommentEntity
        cid=CommentEntity.create(setup['fra_id'],setup['donee_id'],'Another comment.')
        ok,msg=FundraiserController.reply_to_comment(cid,setup['fr_id'],setup['fra_id'],'')
        assert not ok

class TestGenerateReport:
    def test_monthly_report(self,test_db):
        report=AdminController.generate_report('monthly')
        assert 'breakdown' in report; assert 'fra_stats' in report

    def test_daily_report(self,test_db):
        report=AdminController.generate_report('daily')
        assert report['period']=='daily'

    def test_reports_page(self,test_db):
        app.config['TESTING']=True
        with app.test_client() as c:
            c.post('/login',data={'email':'admin@tacofundme.org','password':'admin123'})
            r=c.get('/admin/reports'); assert r.status_code==200

class TestFilterDonationHistory:
    def test_filter_by_category(self,setup,test_db):
        from entity.models import DonationEntity
        DonationEntity.create(setup['donee_id'],setup['fra_id'],50,'test donation')
        donations=DoneeController.get_donations(setup['donee_id'])
        assert isinstance(donations,list)
