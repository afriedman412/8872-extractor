from flask_testing import TestCase

from app import app


class TestFolio(TestCase):
    def create_app(self):
        return app

    def test_home_route(self):
        response = self.client.get("/")
        self.assert200(response)
