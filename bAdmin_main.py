from flask import Flask, jsonify, request, abort, make_response, send_file
from flask.ext.cors import CORS
from datetime import datetime
from datetime import timedelta
import dateutil.parser

app = Flask(__name__)
CORS(app)


database = {"brugere": [{"id": 0, "name": "Anton", "clubs": [], "email": "", "phone": 12345678}, {"id": 1, "name": "Huggo", "clubs": [], "email": "", "phone": 12345678}, {"id": 2, "name": "Træner Kvinde", "clubs": [0, 1], "email": "", "phone": 12345678}, {"id": 3, "name": "Træner Mand", "clubs": [0], "email": "", "phone": 12345678}], #{"id": 905226362922379, "name": "Mark Surrow", "clubs": [0, 1], "email": "msurrow@gmail.com", "phone": 60131201}
            "klubber": [{"id": 0, "name": "FooKlub", "admins": [2], "coaches": [2, 3], "membershipRequests": []}, {"id": 1, "name": "BarKlub", "admins": [1, 905226362922379], "coaches": [2, 905226362922379], "membershipRequests": [0, 1]}, {"id": 2, "name": "Andeby Badmintonklub", "admins": [], "coaches": [], "membershipRequests": []}],
            "traeningspas": [{"id": 0, "name": "A-træning", "club": 0, "startTime": datetime(2016, 12, 24, 18, 00, 00).isoformat(), "durationMinutes": 120, "invited": [0, 1, 905226362922379], "confirmed": [], "rejected": []}, {"id": 1, "name": "B-træning", "club": 0, "startTime": datetime(2016, 12, 31, 18, 00, 00).isoformat(), "durationMinutes": 120, "invited": [0, 1, 905226362922379], "confirmed": [], "rejected": []}, {"id": 2, "name": "A-træning", "club": 1, "startTime": datetime(2016, 12, 24, 19, 30, 00).isoformat(), "durationMinutes": 120, "invited": [0, 1, 905226362922379], "confirmed": [], "rejected": []}]}


@app.route("/")
def index():
    return send_file("templates/index.html")


"""
Brugere
Bruger datatype:
{
    id: <int>, not null
    name: <string>, not null
    clubs: <list:int>, int must be id of existing Klub
    email: <string>, valid email
    phone: <int:8>, 8-digits valid DK phonenumber
}
"""
@app.route("/brugere", methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if not request.json or 'userId' not in request.json or 'name' not in request.json or len(request.json['name']) < 1:
            abort(400)
        else:
            try:
                # Check if the user exits
                bruger = [bruger for bruger in database["brugere"] if bruger["id"] == int(request.json['userId'])]
                if len(bruger) == 0:
                    # A user is created without a club, as they have to apply for
                    # membership (ie. access to) to a club
                    bruger = {"id": int(request.json['userId']),
                              "name": request.json['name'],
                              "clubs": [],
                              "email": request.json['email'],
                              "phone": ""}

                    database["brugere"].append(bruger)

                    return jsonify(bruger)
                else:
                    # Consider it an error to POST (create) to an existing user object
                    abort(400)
            except TypeError:
                abort(400)
    # GET
    else:
        return jsonify(database["brugere"])

@app.route("/brugere/<int:userId>", methods=['GET', 'PUT'])
def user(userId):
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    bruger = [bruger for bruger in database["brugere"] if bruger["id"] == userId]
    if len(bruger) == 0:
        abort(404)

    if request.method == 'PUT':
        if not request.json:
            abort(400)

        newName = bruger[0]['name']
        newClubs = bruger[0]['clubs']
        newEmail = bruger[0]['email']
        newPhone = bruger[0]['phone']

        # Are we updating name? If so, validate and update
        if 'name' in request.json:
            # Don't allow empty name
            if request.json['name'] is "" or len(request.json['name']) < 1:
                abort(400)
            else:
                newName = request.json['name']

        # Are we updating admins list? If so, validate and update. Overwrite
        # existing with input
        if 'clubs' in request.json:
            # A club must have at least one admin, and all admins in list are
            # users
            if not isinstance(request.json['clubs'], list) or not doesAllUsersInListExist(request.json['clubs']):
                abort(400)
            else:
                newClubs = request.json['clubs']

        # Are we updating name? If so, validate and update
        if 'email' in request.json:
            # Don't allow empty name
            if request.json['email'] is "" or len(request.json['email']) < 1:
                abort(400)
            else:
                newEmail = request.json['email']

        # Are we updating name? If so, validate and update
        if 'phone' in request.json:
            # Don't allow empty name
            if request.json['phone'] is "" or len(request.json['phone']) < 1:
                abort(400)
            else:
                newPhone = request.json['phone']

        bruger[0]['name'] = newName
        bruger[0]['clubs'] = newClubs
        bruger[0]['email'] = newEmail
        bruger[0]['phone'] = newPhone

        return jsonify(bruger[0])
    else:
        # GET
        return jsonify(bruger[0])

@app.route("/brugere/<int:userId>/traeningspas", methods=['GET'])
def userPractices(userId):
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    try:
        if not userId or not int(userId):
            abort(404)
    except TypeError:
        abort(400)

    return jsonify([tp for tp in database["traeningspas"] if userId in tp["invited"] or userId in tp["confirmed"] or userId in tp["rejected"]]);

"""
Klubber
Klub datatype:
{
    id: <int>, not null
    name: <string>, not null
    admins: <list:int>, not empty, int must be id of existing Bruger
    coaches: <list:int>, int must be id of existing Bruger
    membershipRequests: <list:int, int must be id of existing Bruger
}
"""
@app.route("/klubber", methods=['GET', 'POST'])
def clubs():
    if request.method == 'POST':
        if not request.json or 'name' not in request.json or len(request.json['name']) < 1:
            abort(400)

       # Are we updating name? If so, validate and update
        if 'name' in request.json:
            # Don't allow empty name
            if request.json['name'] is "" or len(request.json['name']) < 3:
                abort(400)

        # A club is created without members and coaches, and defaults the admin
        # to the creating user.
        newClubId = database["klubber"][-1]["id"]+1
        klub = {"id": newClubId,
                "name": request.json['name'],
                "admins": request.json['userID'],
                "coaches": [],
                "membershipRequests": []}

        # Since the user created a club, he also needs to be member of the club
        # which is handled in the user object.
        brugere = [bruger for bruger in database["brugere"] if bruger["id"] == int(request.json['userID'])]
        brugere[0]['clubs'].append(newClubId)

        database["klubber"].append(klub)

        return jsonify(klub)
    # GET
    else:
        return jsonify(database["klubber"])

@app.route("/klubber/<int:clubId>", methods=['GET', 'PUT'])
def club(clubId):
    # Does the club exist?
    klub = [klub for klub in database['klubber'] if klub['id'] == clubId]
    if len(klub) == 0:
        abort(404)

    if request.method == 'PUT':
        if not request.json:
            abort(400)

        # Default all values to existing values such that missing values
        # in PUT doesn't result in blank fields.
        newName = klub[0]['name']
        newAdmins = klub[0]['admins']
        newCoaches = klub[0]['coaches']
        newMembershipRequests = klub[0]['membershipRequests']

        # Are we updating name? If so, validate and update
        if 'name' in request.json:
            # Don't allow empty name
            if request.json['name'] is "" or len(request.json['name']) < 1:
                abort(400)
            else:
                newName = request.json['name']

        # Are we updating admins list? If so, validate and update. Overwrite
        # existing with input
        if 'admins' in request.json:
            # A club must have at least one admin, and all admins in list are 
            # users
            if not isinstance(request.json['admins'], list) or len(request.json['admins']) < 1 or not doesAllUsersInListExist(request.json['admins']):
                abort(400)
            else:
                newAdmins = request.json['admins']

        # Are we updating coaches list? If so, validate and update. Overwrite
        # existing with input
        if 'coaches' in request.json:
            # Check all coaches in list are users
            if not isinstance(request.json['coaches'], list) or not doesAllUsersInListExist(request.json['coaches']):
                abort(400)
            else:
                newCoaches = request.json['coaches']

        # Are we updating membership requests list? If so, validate and update.
        # Overwrite existing with input
        if 'membershipRequests' in request.json:
            # Check all requests are from actual users
            if not isinstance(request.json['membershipRequests'], list) or not doesAllUsersInListExist(request.json['membershipRequests']):
                abort(400)
            else:
                newMembershipRequests = request.json['membershipRequests']

        klub[0]['name'] =  newName
        klub[0]['admins'] = newAdmins
        klub[0]['coaches'] = newCoaches
        klub[0]['membershipRequests'] = newMembershipRequests

        return jsonify(klub[0])
    # GET
    else:
        return jsonify(klub[0])

@app.route("/klubber/<int:clubId>/traeningspas", methods=['GET'])
def clubPractices(clubId):
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    if not clubId or not isinstance(int(clubId), int):
        abort(404)

    return jsonify([tp for tp in database["traeningspas"] if clubId is tp["club"]])

@app.route("/klubber/<int:clubId>/medlemmer", methods=['GET'])
def clubMembers(clubId):
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    try:
        int(clubId)
    except TypeError:
        abort(404)

    return jsonify([user for user in database["brugere"] if clubId in user["clubs"]])

"""
Træningspas
Træningspas datatype:
{
    id: <int>, not null
    club: <int>, not null club must be id of existing club
    startTime: <datetime>, not null
    durationMinutes: <int>, int must be >0
    invited: <list:int>, ints must be id of existing user
    confirmed: <list:int>, ints must be id of existing user
    rejected: <list:ing>, ints must be id of existing user
}
"""
@app.route("/traeningspas", methods=['GET', 'POST'])
def practices():
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    if request.method == 'POST':
        if not request.json:
            abort(400)

        # Validate club exists and starttime is valid
        if 'club' in request.json:
            try:
                klub = [klub for klub in database['klubber'] if klub['id'] == int(request.json['club'])]
            except ValueError:
                abort(400)
            if len(klub) == 0:
                abort(400)
        else:
            abort(400)

        # Check practice bame exists and is valid
        if 'name' not in request.json or not isinstance(request.json['name'], str):
            abort(400)

        # Check startTime exists and is valid
        if 'startTime' not in request.json or not dateutil.parser.parse(request.json['startTime']):
            abort(400)

        # Check durationMinutes exists and is valid
        if 'durationMinutes' in request.json:
            try:
                if int(request.json['durationMinutes']) <= 0:
                    abort(400)
            except ValueError:
                abort(400)
        else:
            abort(400)

        # Check invited players are existing users
        if 'invited' not in request.json or not isinstance(request.json['invited'], list) or not doesAllUsersInListExist(request.json['invited']):
            abort(400)

        repeats = 1        
        if 'repeats' in request.json and request.json['repeats'] is not None:
            try:
                if int(request.json['repeats']) <= 0 or int(request.json['repeats']) > 51:
                    abort(400)
                else:
                    repeats = int(request.json['repeats'])
            except TypeError:
                abort(400)

        # A practice is created without confirmed or rejected invitees
        print(request.json)
        pDate = dateutil.parser.parse(request.json['startTime'])
        print(pDate)

        for x in range(0, repeats):
            traeningspas = {"id": database["traeningspas"][-1]["id"]+1,
                            "name": request.json['name'],
                            "club": int(request.json['club']),
                            "startTime": pDate,
                            "durationMinutes": request.json['durationMinutes'],
                            "invited": request.json['invited'],
                            "confirmed": [],
                            "rejected": []}
            database["traeningspas"].append(traeningspas)
            # Add one week to the date
            pDate = pDate + timedelta(weeks=1)

        return jsonify(traeningspas)
    # GET
    else:
        return jsonify(database["traeningspas"])

@app.route("/traeningspas/<int:practiceId>", methods=['GET', 'PUT', 'DELETE'])
def practice(practiceId):
   
    # Does the træningspas exist?
    traeningspas = [traeningspas for traeningspas in database['traeningspas'] if traeningspas['id'] == practiceId]
    if len(traeningspas) == 0:
        abort(404)

    if request.method == 'PUT':
        if not request.json:
            abort(400)
        # Design decision: cannot updated clubId.

        newStartTime = traeningspas[0]['startTime']
        newDurationMinutes = traeningspas[0]['durationMinutes']
        newInvited = traeningspas[0]['invited']
        newConfirmed = traeningspas[0]['confirmed']
        newRejected = traeningspas[0]['rejected']

        # Are we updating start time? If so, validate and update
        if 'startTime' in request.json:
            # Start time must be a valid date
            if datetime(request.json['startTime']):
                newStartTime = datetime(request.json['startTime'])
            else:
                abort(400)

        # Are we updating traeningspas duration? If so, validate and update.
        if 'durationMinutes' in request.json:
            # A duration must be >0 minutes
            if isinstance(request.json['durationMinutes'], int) and request.json['durationMinutes'] <= 0:
                newDurationMinutes = request.json['durationMinutes']
            else:
                abort(400)

        # Are we updating invited players list? If so, validate and update.
        # Overwrite existing with input
        if 'invited' in request.json:
            # Check all players in list are users
            if isinstance(request.json['invited'], list) and doesAllUsersInListExist(request.json['invited']):
                newInvited = request.json['invited']
            else:
                abort(400)

        # Are we updating confirmed players list? If so, validate and update.
        # Overwrite existing with input
        if 'confirmed' in request.json:
            # Check all confirmed players are actual users
            if isinstance(request.json['confirmed'], list) and doesAllUsersInListExist(request.json['confirmed']):
                newConfirmed = request.json['confirmed']
            else:
                abort(400)

        # Are we updating rejected players list? If so, validate and update.
        # Overwrite existing with input
        if 'rejected' in request.json:
            # Check all confirmed players are actual users
            if isinstance(request.json['rejected'], list) and doesAllUsersInListExist(request.json['rejected']):
                newRejected = request.json['rejected']
            else:
                abort(400)

        traeningspas[0]['startTime'] = newStartTime
        traeningspas[0]['durationMinutes'] = newDurationMinutes
        traeningspas[0]['invited'] = newInvited
        traeningspas[0]['confirmed'] = newConfirmed
        traeningspas[0]['rejected'] = newRejected

        return jsonify(traeningspas[0])

    if request.method == 'DELETE':
        obj = None
        pId = -1
        try:
            pId = int(practiceId)
        except TypeError:
            abort(400)

        for tp in database["traeningspas"]:
            if tp["id"] is pId:
                obj = tp
                break

        if obj is not None:
            database["traeningspas"].remove(obj)

        return jsonify("")
    # GET
    else:
        return jsonify(traeningspas[0])

"""
Helpers and error handlers
"""
def doesUserExist(userId):
    bruger = [bruger for bruger in database["brugere"] if bruger["id"] == int(userId)]
    if len(bruger) == 0:
        return False
    else:
        return True

def doesAllUsersInListExist(userIDList):
    if not isinstance(userIDList, list):
        app.logger.warning("Called doesAllUsersInListExist with param that is not a list: ", userIDList)

    for bruger in userIDList:
        if not doesUserExist(bruger):
            return False
    return True

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
