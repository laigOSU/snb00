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
            url = "http://localhost:8080/boats/" + str(e.key.id)
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
        key = client.key(constants.boats, int(id))
        client.delete(key)
        # print("testing query filter")
        # query = client.query(kind=constants.boats)
        # first_key = client.key(constants.boats,5660980839186432)
        # query.key_filter(first_key,'=')
        # # query.add_filter(key.id, '=', '5660980839186432')
        # queryresults = list(query.fetch())
        # # return queryresults["name"]
        # print(queryresults)
        # for e in queryresults:
        #     print("name is ", e["name"])
        #     print("id is ", e.key.id)
        #     find_boat_key = e.key.id
        #     print("find_boat_key is ", find_boat_key)
        # print("second query by find_boat_key")
        # query2 = client.query(kind=constants.boats)
        # second_key = client.key(constants.boats, find_boat_key)
        # query2.key_filter(second_key,'=')
        # findboatresults = list(query2.fetch())
        # getboatkey = client.key(constants.boats, find_boat_key)
        # print("getboatkey is ", getboatkey)
        # foundboat = client.get(key=getboatkey)
        # foundboat["name"] = "changing the name of this found boat"
        # print("foundboat is now: ", foundboat)
        # client.put(foundboat)
        # return (json.dumps(findboatresults))
        return ('',200)

    #---- GET: VIEW A SPECIFIC BOAT ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        first_key = client.key(constants.boats,int(id))
        query.key_filter(first_key,'=')
        results = list(query.fetch())
        for e in results:
            e["id"] = id
            url = "http://localhost:8080/boats/" + id
            e["boat_url"] =url
        return json.dumps(results)
        # results = json.dumps(requested_boat)
        # url = "http://localhost:8080/" + id
        # output = "live link: " + url + ";\n" + results
        # return (output)

    else:
        return 'Method not recognized'
