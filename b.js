from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST','GET'])
# def guests_get_post():
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(new_boat)
        return str(new_boat.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            url = "http://localhost:8080/boats/" + str(e.key.id)
            e["live link"] =url
        return json.dumps(results)
    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PUT','DELETE','GET'])
def boats_put_delete_get(id):
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], 'type': content['type'], 'length': content['length']})
        client.put(boat)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.boats, int(id))
        client.delete(key)
        return ('',200)
    elif request.method == 'GET':
        my_boat_key = client.key(constants.boats, int(id))
        requested_boat = client.get(key=my_boat_key)
        results = json.dumps(requested_boat)
        print("testing query filter")
        query = client.query(kind=constants.boats)
        first_key = client.key(constants.boats,5660980839186432)
        query.key_filter(first_key,'=')
        # query.add_filter(key.id, '=', '5660980839186432')
        queryresults = list(query.fetch())
        # return queryresults["name"]
        print(queryresults)
        for e in queryresults:
            print("name is ", e["name"])
            print("id is ", e.key.id)
            find_boat_key = e.key.id
            print("find_boat_key is ", find_boat_key)
        print("second query by find_boat_key")
        query2 = client.query(kind=constants.boats)
        second_key = client.key(constants.boats, find_boat_key)
        query2.key_filter(second_key,'=')
        findboatresults = list(query2.fetch())
        return (json.dumps(findboatresults))
        # return (json.dumps(queryresults))
    else:
        return 'Method not recognized'
