from flask import Flask, jsonify, request, abort, make_response, send_file
from flask.ext.cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

database = {"brugere": [{"id": 0, "name": "Anton", "clubs": [], "email": "", "phone": 12345678}, {"id": 1, "name": "Huggo", "clubs": [], "email": "", "phone": 12345678}, {"id": 2, "name": "Træner Kvinde", "clubs": [0, 1], "email": "", "phone": 12345678}, {"id": 3, "name": "Træner Mand", "clubs": [0], "email": "", "phone": 12345678}, {"id": 905226362922379, "name": "Mark Surrow", "clubs": [], "email": "msurrow@gmail.com", "phone": 60131201}], 
            "klubber": [{"id": 0, "name": "FooKlub", "admins": [], "coaches": [], "membershipRequests": []}, {"id": 1, "name": "BarKlub", "admins": [1], "coaches": [1], "membershipRequests": []}],
            "traeningspas": [{"id": 0, "club": 0, "startTime": datetime(2016, 12, 24, 18, 00, 00), "durationMinutes": 120, "invited": [0, 1], "confirmed": [0]}]}

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
        if not request.json or 'name' not in request.json or len(request.json['name']) < 1:
            abort(400)
        else:
            # A user is created without a club, as they have to apply for
            # membership (ie. access to) to a club
            bruger = {"id": database["brugere"][-1]["id"]+1,
                      "name": request.json['name'],
                      "clubs": [],
                      "email": request.json['email'],
                      "phone": request.json['phone']}

            database["brugere"].append(bruger)

            return jsonify(bruger)
    # GET
    else:
        return jsonify(database["brugere"])

@app.route("/brugere/<int:userId>", methods=['GET'])
def user(userId):
    print("Auth dummy: ", request.args.get('userID'), ", ", request.args.get('userAccessToken'))

    bruger = [bruger for bruger in database["brugere"] if bruger["id"] == userId]
    if len(bruger) == 0:
        abort(404)

    return jsonify(bruger[0])

@app.route("/brugere/<int:userId>/traeningspas", methods=['GET'])
def userTraeningspas(userId):
    # TODO: Test cases
    return jsonify({})

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

        # Check request have admin list with atleast one admin. Validate
        # user(s) for admin(s) exists
        if 'admins' in request.json and isinstance(request.json['admins'], list) and len(request.json['admins']) > 0:
            if not doesAllUsersInListExist(request.json['admins']):
                abort(400)
        else:
            abort(400)

        # A club is created without members and coaches, and defaults the admin
        # to the creating user.
        klub = {"id": database["klubber"][-1]["id"]+1,
                "name": request.json['name'],
                "admins": request.json['admins'],
                "coaches": [],
                "membershipRequests": []}

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

"""
Træningspas
Træningspas datatype:
{
    id: <int>, not null
    club: <int>, not null club must be id of existing club
    startTime: <datetime>, not null
    durationMinutes: <int>, int must be >0
    invited: <list:int>, ints must be id of existing Spiller
    confirmed: <list:int>, ints must be id of existing Spiller
}
"""
@app.route("/traeningspas", methods=['GET', 'POST'])
def practices():
    if request.method == 'POST':
        if not request.json:
            abort(400)

        # Validate club exists and starttime is valid
        if 'club' in request.json:
            klub = [klub for klub in database['klubber'] if klub['id'] == request.json['club']]
            if len(klub) == 0:
                abort(404)
        else:
            abort(400)

        # Check startTime exists and is valid
        if 'startTime' not in request.json or not datetime(request.json['startTime']):
            abort(400)

        # Check durationMinutes exists and is valid
        if 'durationMinutes' not in request.json or not isinstance(request.json['durationMinutes'], int) or request.json['durationMinutes'] <= 0:
            abort(400)

        # Check invited players are existing users
        if 'invited' not in request.json or not isinstance(request.json['invited'], list) or not doesAllUsersInListExist(request.json['invited']):
            abort(400)

        # Check confirmed players are existing users
        if 'confirmed' not in request.json or not doesAllUsersInListExist(request.json['confirmed']):
            abort(400)

        # A practice is created without confirmed invitees
        traeningspas = {"id": database["traeningspas"][-1]["id"]+1,
                        "club": request.json['club'],
                        "startTime": datetime(request.json['startTime']),
                        "durationMinutes": request.json['durationMinutes'],
                        "invited": request.json['invited'],
                        "confirmed": []}

        database["traeningspas"].append(traeningspas)

        return jsonify(traeningspas)
    # GET
    else:
        return jsonify(database["traeningspas"])

@app.route("/traeningspas/<int:practiceId>", methods=['GET', 'PUT'])
def practice(practiceId):
    # Does the træningspas exist?
    traeningspas = [traeningspas for traeningspas in database['træningspas'] if traeningspas['id'] == practiceId]
    if len(traeningspas) == 0:
        abort(404)

    if request.method == 'PUT':
        if not request.json:
            abort(400)
        # Design decision: cannot updated clubId.

        # Are we updating start time? If so, validate and update
        if 'startTime' in request.json:
            # Start time must be a valid date
            if datetime(request.json['startTime']):
                traeningspas[0]['startTime'] = datetime(request.json['startTime'])
            else:
                abort(400)

        # Are we updating traeningspas duration? If so, validate and update.
        if 'durationMinutes' in request.json:
            # A duration must be >0 minutes
            if isinstance(request.json['durationMinutes'], int) and request.json['durationMinutes'] <= 0:
                traeningspas[0]['durationMinutes'] = request.json['durationMinutes']
            else:
                abort(400)

        # Are we updating invited players list? If so, validate and update.
        # Overwrite existing with input
        if 'invited' in request.json:
            # Check all players in list are users
            if isinstance(request.json['invited'], list) and doesAllUsersInListExist(request.json['invited']):
                traeningspas[0]['invited'] = request.json['invited']
            else:
                abort(400)

        # Are we updating confirmed players list? If so, validate and update.
        # Overwrite existing with input
        if 'confirmed' in request.json:
            # Check all confirmed players are actual users
            if isinstance(request.json['confirmed'], list) and doesAllUsersInListExist(request.json['confirmed']):
                traeningspas[0]['confirmed'] = request.json['confirmed']
            else:
                abort(400)

        return jsonify(traeningspas[0])
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
