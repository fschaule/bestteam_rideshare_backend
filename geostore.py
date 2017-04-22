from flask import Flask, request
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from pymongo import MongoClient, GEO2D
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from bson.son import SON

app = Flask(__name__)
api = Api(app)
mongo = PyMongo(app)
geolocator = Nominatim()

db = MongoClient('localhost', 27017).geo_example
db.places.create_index([("loc", GEO2D)])


class GeoDB():
    distance = 20  # 20 km distance

    @staticmethod
    def insert(user_id, request_status, start_location, end_location):
        result = db.places.insert_one({"loc": [start_location.latitude, start_location.longitude], "user_id": user_id,
                                       "ride_status": request_status,
                                       "loc_end": [end_location.latitude, end_location.longitude]})
        print("inserted in db: " + str(result))

    @staticmethod
    def match(lat, lon):
        degree_distance = GeoDB.distance / 111.12
        result = db.places.find({"loc": SON([("$near", [lat, lon]), ("$maxDistance", degree_distance)])})

        return result

    @staticmethod
    def findRides(user_id, request_status, start_location, end_location):
        possible_set = GeoDB.match(start_location.latitude, start_location.longitude)
        for item in possible_set:
            print("possible result: " + str(item))
            if item["user_id"] != user_id:
                ride_end_location = (item["loc_end"][0], item["loc_end"][1])
                if vincenty(ride_end_location, (end_location.latitude, end_location.longitude)).kilometers < GeoDB.distance:
                    print("result: " + str(item))


class DataInferace(Resource):
    def post(self):
        json_content = request.json

        request_status = json_content["request_status"]
        user_id = json_content["user_id"]
        start_location = geolocator.geocode(json_content["start"]["location"])
        end_location = geolocator.geocode(json_content["end"]["location"])
        print("start lat " + str(start_location.latitude) + "lon " + str(start_location.longitude))
        print("end lat " + str(end_location.latitude) + "lon " + str(end_location.longitude))
        GeoDB.insert(user_id, request_status, start_location, end_location)

        if (request_status == "request"):
            GeoDB.findRides(user_id, request_status, start_location, end_location)


class Test(Resource):
    def get(self):
        return "test"


api.add_resource(DataInferace, '/ride_location')
api.add_resource(Test, '/test')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
