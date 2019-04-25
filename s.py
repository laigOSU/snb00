from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('slip', __name__, url_prefix='/slips')

@bp.route('', methods=['POST','GET'])
def slips_get_post():
    #---- POST: CREATE A NEW SLIP ----#
    if request.method == 'POST':
        content = request.get_json()
        new_slip = datastore.entity.Entity(key=client.key(constants.slips))
        new_slip.update({'number': content['number'], 'current_boat': 'null', 'arrival_date': "null"})
        client.put(new_slip)
        return str(new_slip.key.id)

    #---- GET: VIEW ALL SLIPS ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            url = "http://localhost:8080/slips/" + str(e.key.id)
            e["slip_url"] =url
        return json.dumps(results)

    else:
        return 'Method not recogonized'

@bp.route('/<id>', methods=['PUT','DELETE'])
def slips_put_delete(id):
    #---- PUT: MODIFY A SPECIFIC SLIP ----#
    if request.method == 'PUT':

        # Trying to assign a boat to an occupied slip produces a 403 error
        # Get the input
        content = request.get_json()

        # Get the slip
        slip_key = client.key(constants.slips, int(id))
        my_slip = client.get(key=slip_key)
        print("my_slip[current_boat] is: ", my_slip["current_boat"])

        # my_slip.update({"number": content["number"], "current_boat": content["current_boat"],
        #   "arrival_date": content["arrival_date"]})

        print("my_slip is: ", my_slip)
        print("my_slip.keys() is: ", my_slip.keys())
        # print("my_slip.keys()[current_boat] is", my_slip.keys()[current_boat])


        if content["current_boat"] != "null" and my_slip["current_boat"] != "null":
            return ('This slip is already occupied',403)
        else:
            my_slip.update({"number": content["number"], "current_boat": content["current_boat"],
              "arrival_date": content["arrival_date"]})
            client.put(my_slip)
            return('Modification entered',200)



        # print("user sent current_boat as: ", content["current_boat"])
        # print("my_slip is: ", my_slip)
        # currboat = my_slip["current_boat"]
        # print("current boat is: ", currboat)
        # check if current_boat != null

        # my_slip.update({"number": content["number"], "current_boat": content["current_boat"],
        #   "arrival_date": content["arrival_date"]})
        # client.put(slip)

        # return ("current boat is: ", currboat)


    #---- DELETE: REMOVE A SPECIFIC SLIP ----#
    elif request.method == 'DELETE':
        key = client.key(constants.slips, int(id))
        client.delete(key)
        return ('',200)

    #---- GET: VIEW A SPECIFIC SLIP ----#
    elif request.method == 'GET':
        # TODO -->>>> Also check if current_boat != null, then get the boat_ID and simply print boat_url

        # Get the specific slip
        query = client.query(kind=constants.slips)
        first_key = client.key(constants.slips,int(id))
        query.key_filter(first_key,'=')
        results = list(query.fetch())
        for e in results:
            e["id"] = id
            url = "http://localhost:8080/slips/" + id
            e["slip_url"] =url
        return json.dumps(results)

    else:
        return 'Method not recogonized'

@bp.route('/<lid>/boats/<gid>', methods=['PUT','DELETE'])
def add_delete_reservation(lid,gid):
    if request.method == 'PUT':
        slip_key = client.key(constants.slips, int(lid))
        slip = client.get(key=slip_key)
        boat_key = client.key(constants.boats, int(gid))
        boat = client.get(key=boat_key)
        if 'boats' in slip.keys():
            slip['boats'].append(boat.id)
        else:
            slip['boats'] = [boat.id]
        client.put(slip)
        return('',200)
    if request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(lid))
        slip = client.get(key=slip_key)
        if 'boats' in slip.keys():
            slip['boats'].remove(int(gid))
            client.put(slip)
        return('',200)

@bp.route('/<id>/boats', methods=['GET'])
def get_reservations(id):
    slip_key = client.key(constants.slips, int(id))
    slip = client.get(key=slip_key)
    boat_list  = []
    if 'boats' in slip.keys():
        for gid in slip['boats']:
            boat_key = client.key(constants.boats, int(gid))
            boat_list.append(boat_key)
        return json.dumps(client.get_multi(boat_list))
    else:
        return json.dumps([])
