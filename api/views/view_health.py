from flask_restful import Resource


class ViewHealth(Resource):
    def get(self):
        return 'ok', 200
