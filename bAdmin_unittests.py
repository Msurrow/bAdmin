import bAdmin_main
import unittest
import json

class bAdminTestUsers(unittest.TestCase):
    def setUp(self):
        bAdmin_main.app.config['TESTING'] = True
        self.app = bAdmin_main.app.test_client()

    def tearDown(self):
        pass

    def test_users_GET(self):
        res = self.app.get("/brugere")
        jres = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(jres[0]['id'],0)
        self.assertEqual(jres[0]['name'],"Anton")

    def test_users_POST_nodata(self):
        res = self.app.post("/brugere", data=json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_users_POST_userHasName(self):
        res = self.app.post("/brugere", data=json.dumps({'name_wrong':""}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_users_POST_userHasNameNotNothing(self):
        res = self.app.post("/brugere", data=json.dumps({'name':""}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_users_POST_userIsCreated(self):
        res1 = self.app.get("/brugere")
        jres1 = json.loads(res1.data.decode())
        lastUser = jres1[-1]['id']
        self.assertEqual(lastUser, 905226362922379)

        name = "Foobar"
        email = "foo@gmail.com"
        phone = "11223344"
        clubs = "[1,2]"

        res2 = self.app.post("/brugere", data=json.dumps({'name':name, 'email':email, 'phone':phone, 'clubs':clubs}), content_type='application/json')
        jres2 = json.loads(res2.data.decode())
        lastUser2 = jres2
        self.assertEqual(lastUser2["id"], lastUser+1)
        self.assertEqual(lastUser2["name"], name)
        self.assertEqual(lastUser2["email"], email)
        self.assertEqual(len(lastUser2["clubs"]), 0) # A user is created with 0 clubs and input arg is ignored

    def test_user_GET_userExists(self):
        res = self.app.get("/brugere/0")
        jres = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(jres['id'],0)

    def test_user_GET_userDoesntExist(self):
        res = self.app.get("/brugere/5")
        self.assertEqual(res.status_code, 404)

class bAdminTestClubs(unittest.TestCase):
    def setUp(self):
        bAdmin_main.app.config['TESTING'] = True
        self.app = bAdmin_main.app.test_client()

    def tearDown(self):
        pass

    def test_clubs_GET(self):
        res = self.app.get("/klubber")
        jres = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(jres),2)

    def test_clubs_POST_nodata(self):
        res = self.app.post("/klubber", data=json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_clubs_POST_clubHasNameNotNothing(self):
        res = self.app.post("/klubber", data=json.dumps({'name':""}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_clubs_POST_clubHasAdminlist(self):
        res = self.app.post("/klubber", data=json.dumps({'admin_wrong':[]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_clubs_POST_clubHasAdminlistNotEmpty(self):
        res = self.app.post("/klubber", data=json.dumps({'admin':[]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_clubs_POST_clubHasAdminlistUsersExist(self):
        res = self.app.post("/klubber", data=json.dumps({'admin':[99]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_clubs_POST_clusIsCreated(self):
        res1 = self.app.get("/klubber")
        jres1 = json.loads(res1.data.decode())
        c1 = jres1[-1]['id']
        self.assertEqual(c1, 1)

        name = "Foobar"
        admins = [0]
        coaches = [1,2]
        membershipRequests = [1,2]

        res2 = self.app.post("/klubber", data=json.dumps({'name':name, 'admins':admins, 'coaches':coaches, 'membershipRequests':membershipRequests}), content_type='application/json')
        jres2 = json.loads(res2.data.decode())
        c2 = jres2
        self.assertEqual(c2["id"], c1+1)
        self.assertEqual(c2["name"], name)
        self.assertEqual(c2["admins"], admins)

        self.assertEqual(len(c2["coaches"]), 0) # A bluc is created with 0 coaches and input arg is ignored
        self.assertEqual(len(c2["membershipRequests"]), 0) # A bluc is created with 0 membershiprequests and input arg is ignored

    def test_club_GET_clubExists(self):
        res = self.app.get("/klubber/0")
        jres = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(jres['id'],0)

    def test_club_GET_clubDoesntExist(self):
        res = self.app.get("/klubber/99")
        self.assertEqual(res.status_code, 404)

    def test_club_PUT_hasData(self):
        res = self.app.put("/klubber/0", data=json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_club_PUT_nameIsValid(self):
        res = self.app.put("/klubber/0", data=json.dumps({'name':""}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_club_PUT_adminsIsValid(self):
        res = self.app.put("/klubber/0", data=json.dumps({'admins': [99]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.app.put("/klubber/0", data=json.dumps({'admins': []}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.app.put("/klubber/0", data=json.dumps({'admins': 'notalist'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_club_PUT_coachesIsValid(self):
        res = self.app.put("/klubber/0", data=json.dumps({'coaches': [99]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.app.put("/klubber/0", data=json.dumps({'coaches': 'notalist'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_club_PUT_membershipRequestsIsValid(self):
        res = self.app.put("/klubber/0", data=json.dumps({'membershipRequests': [99]}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        res = self.app.put("/klubber/0", data=json.dumps({'membershipRequests': 'notalist'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_club_PUT_clubIsUpdated(self):
        res = self.app.get("/klubber/0")
        c = json.loads(res.data.decode())

        name = "New Name"
        admins = [0]
        coaches = [0,1]
        membershipRequests = [0]
        res2 = self.app.put("/klubber/0", data=json.dumps({'name': name,
                                                           'admins': admins,
                                                           'coaches': coaches,
                                                           'membershipRequests': membershipRequests}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        c2 = json.loads(res2.data.decode())
        self.assertEqual(c2['name'], name)
        self.assertEqual(c2['admins'], admins)
        self.assertEqual(c2['coaches'], coaches)
        self.assertEqual(c2['membershipRequests'], membershipRequests)

class bAdminTestPractices(unittest.TestCase):
    def setUp(self):
        bAdmin_main.app.config['TESTING'] = True
        self.app = bAdmin_main.app.test_client()

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
