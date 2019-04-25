from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST','GET'])
def boats_get_post():
    #---- POST: CREATE A NEW BOAT ----#
    if request.method == 'POST':
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(new_boat)
        return str(new_boat.key.id)

    #---- GET: VIEW ALL BOATS ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            # url = "http://localhost:8080/boats/" + str(e.key.id)
            url = constants.local_url + constants.boats + "/" + str(e.key.id)
            e["boat_url"] =url
        return json.dumps(results)

    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PUT','DELETE','GET'])
def boats_put_delete_get(id):
    #---- PUT: MODIFY A SPECIFIC BOAT ----#
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(boat)
        return ('',200)

    #---- DELETE: REMOVE A SPECIFIC BOAT ----#
    elif request.method == 'DELETE':
        # Get the boat
        key = client.key(constants.boats, int(id))

        # Check if boat is docked in a slip --> if boat_id == slip["current_boat"]
        # Get that slip
        query = client.query(kind=constants.slips)
        query.add_filter('current_boat', '=', id)
        queryresults = list(query.fetch())
        print("queryresults is: ", queryresults)
        for e in queryresults:
            print("number is: ", e["number"])
            print("current_boat is: ", e["current_boat"])
            print("slip id is: ", e.key.id)
            slip_id = e.key.id

            slip_key = client.key(constants.slips, slip_id)
            slip = client.get(key=slip_key)
            slip["current_boat"] = "null"
            slip["arrival_date"] = "null"
            client.put(slip)
        client.delete(key)

        return ('',200)

    #---- GET: VIEW A SPECIFIC BOAT ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        first_key = client.key(constants.boats,int(id))
        query.key_filter(first_key,'=')
        results = list(query.fetch())
        for e in results:
            e["id"] = id
            # url = "http://localhost:8080/boats/" + id
            url = constants.local_url + constants.boats + "/" + id
            e["boat_url"] =url
        return json.dumps(results)


    else:
        return 'Method not recognized'
