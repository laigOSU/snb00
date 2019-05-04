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
        boat_id = str(new_boat.key.id)
        url = constants.appspot_url + constants.boats + "/" + boat_id
        new_boat["self"] = url
        client.put(new_boat)
        return (str(new_boat.key.id), 201)

    #---- GET: VIEW ALL BOATS ----#
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            # url = "http://localhost:8080/boats/" + str(e.key.id)
            # url = constants.appspot_url + constants.boats + "/" + str(e.key.id)
            # e["boat_url"] =url
        print("Viewing all boats.")
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
            # url = constants.appspot_url + constants.boats + "/" + id
            # e["boat_url"] =url
        print("Viewing specific boat #", id)
        return json.dumps(results)

    else:
        return 'Method not recognized'

@bp.route('/<bid>/cargos/<cid>', methods=['PUT','DELETE'])
def add_delete_docking(bid,cid):
    #---- PUT: APPEND A CARGO ONTO THIS BOAT ----#
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(bid))
        boat = client.get(key=boat_key)
        cargo_key = client.key(constants.cargos, int(cid))
        cargo = client.get(key=cargo_key)


        cargo_json = {"id": cargo.id, "self": cargo["self"]}

        print("cargo[carrier] is: ",cargo["carrier"])
        print("cargo[carrier][name] is: ",cargo["carrier"]["name"])
        print("cargo[carrier][id] is: ", cargo["carrier"]["id"])
        print("cargo id passed in is: ", cid)
        print("cargo is: ", cargo)
        # Check if cargo not yet assigned to any boat
        if cargo["carrier"]["name"] == "null":
            print("Cargo not yet assigned to any ship. So append (or add).")

            if 'cargo' in boat.keys():
                # boat['cargo'].append(cargo_json)
                print("Appending subsequent cargo to this boat")
            else:
                # boat['cargo'] = [cargo_json]
                print("Adding first cargo to this boat.")
            # client.put(boat)


            # Update cargo[carrier] to = boat

            # cargo["carrier"].update({'name': boat["name"], self: boat["self"], "id": bid })
            # print("boat[id]: ", boat["id"])
            # print("boat[name]: ", boat["name"])

            print("boat: ", boat)
            print("boat.key.id: ", boat.key.id)
            print("boat[name]: ", boat["name"])
            print("boat[self]: ", boat["self"])
            # client.put(cargo)

            return("Cargo loaded", 200)
        else:
            print("Cargo already assigned to a boat, cannot load here.")
            return("Cargo already assigned to a boat.", 403)
            # If the cargo is already assigned to another boat, you cannot
            # assign it to this boat. Throw 403 error.
            # print("boat[cargo][id]: ", boat["cargo"]["id"])
            # print("type of boat[cargo][id]: ", type(boat["cargo"]["id"]))
            # print("cargo.key.id is: ", cargo.key.id)
            # print("type of cargo.key.id is: ", type(cargo.key.id))


            # cargo_loaded = False
            # print("boat[cargo] is: ", boat["cargo"])
            # for e in boat["cargo"]:
            #     print(e["id"])
            #     print(e["self"])
            #     # if e["id"] == cargo.key.id:
            #     if int(cid) == e["id"]:
            #         print("Cargo ", int(cid), "is already loaded on this boat")
            #         cargo_loaded = True
            #     # else:
            #     #     print("Cargo ", int(cid), "is NOT yet loaded on this boat")
            # if cargo_loaded == True:
            #        print("Cargo ", cid ," already loaded. Print a 403 error here.")
            # else:
            #     print("Cargo ", cid, " not yet loaded. Append here.")
                    # # boat['cargo'].append(cargo_json)
            # for e in boat["cargo"]:
            #     print("e[self] is: ",str(e["id"]))
            # if '5740315998683136'in boat["cargo"]:
            #     print("5740315998683136 is in boat[cargo]")
            # else:
            #     print("5740315998683136 NOT in boat[cargo]")

            # if boat['cargo']['id'] == :


    #---- DELETE: REMOVE A SPECIFIC CARGO FROM A BOAT ----#
    if request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(sid))
        slip = client.get(key=slip_key)
        print("slip[current_boat]: ", slip["current_boat"])
        slip["current_boat"] = "null"
        slip["arrival_date"] = "null"
        client.put(slip)
        # if 'boats' in slip.keys():
        #     slip['boats'].remove(int(bid))
        #     client.put(slip)
        return('',200)
