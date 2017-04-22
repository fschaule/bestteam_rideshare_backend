from flask import Flask, request
from flask_restful import Resource, Api
from  watson_developer_cloud  import ConversationV1

conversation = ConversationV1(
    username='b6b2699f-0985-41a3-9c2b-3690df8f125f',
    password='nhawoSB1unoT',
    version='2016-09-20')


workspace_id = 'a244c11b-2418-4464-8ca7-fb467e967a3d'

app = Flask(__name__)
api = Api(app)





class ChatInterface(Resource):

    def post(self):
        json_content = request.json

api.add_resource(ChatInterface, '/chat')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)