'''Sprint 3 Tests — Donations, Favourites, Comments.'''
import pytest,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
from entity.models import init_db,FRAEntity,UserEntity,DonationEntity,FRAFavoriteEntity,CommentEntity
from control.controllers import DoneeController,AuthController
from boundary.routes import app

@pytest.fixture(scope='module')
def test_db(tmp_path_factory):
    import entity.models as m
    db=str(tmp_path_factory.mktemp('db')/'test.db'); orig=m.DB_PATH
    m.DB_PATH=db; init_db(); yield db; m.DB_PATH=orig

@pytest.fixture(scope='module')
def active_fra(test_db):
    AuthController.register('FR','fr_s3@test.com','pass123','pass123','fundraiser')
    AuthController.register('Donee','donee_s3@test.com','pass123','pass123','donee')
    fr=UserEntity.find_by_email('fr_s3@test.com')
    fid=FRAEntity.create('Active FRA','Long description for this campaign.',None,1000,fr['id'])
    FRAEntity.update_fields(fid,status='active')
    return fid

@pytest.fixture(scope='module')
def donee_uid(test_db): return UserEntity.find_by_email('donee_s3@test.com')['id']

class TestDonations:
    def test_valid_donation(self,active_fra,donee_uid,test_db):
        ok,msg=DoneeController.donate(active_fra,donee_uid,50,'Great work!')
        assert ok; assert 'successful' in msg

    def test_zero_amount(self,active_fra,donee_uid,test_db):
        ok,msg=DoneeController.donate(active_fra,donee_uid,0,'')
        assert not ok

    def test_negative_amount(self,active_fra,donee_uid,test_db):
        ok,msg=DoneeController.donate(active_fra,donee_uid,-10,'')
        assert not ok

    def test_donation_history(self,donee_uid,test_db):
        donations=DoneeController.get_donations(donee_uid)
        assert isinstance(donations,list)

class TestFavourites:
    def test_toggle_favourite(self,active_fra,donee_uid,test_db):
        added,err=DoneeController.toggle_favorite(active_fra,donee_uid)
        assert err is None; assert added is True

    def test_toggle_removes_favourite(self,active_fra,donee_uid,test_db):
        # Ensure it is favourited first, then toggle off
        from entity.models import FRAFavoriteEntity
        if not FRAFavoriteEntity.is_favorited(donee_uid, active_fra):
            DoneeController.toggle_favorite(active_fra, donee_uid)
        removed,err=DoneeController.toggle_favorite(active_fra,donee_uid)
        assert err is None; assert removed is False

    def test_get_favourites(self,donee_uid,test_db):
        fras=DoneeController.get_favorites(donee_uid)
        assert isinstance(fras,list)

class TestComments:
    def test_add_comment(self,active_fra,donee_uid,test_db):
        ok,msg=DoneeController.add_comment(active_fra,donee_uid,'This is a great initiative!')
        assert ok

    def test_empty_comment(self,active_fra,donee_uid,test_db):
        ok,msg=DoneeController.add_comment(active_fra,donee_uid,'')
        assert not ok
