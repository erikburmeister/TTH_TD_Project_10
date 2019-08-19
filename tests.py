import unittest

import json

import models
from app import app


class DatabaseSetUp(unittest.TestCase):
    def setUp(self):
        models.initialize()
        self.app = app.test_client()

    def tearDown(self):
        models.DATABASE.drop_tables(models.Todo)
        models.DATABASE.close()


class TestWebApp(DatabaseSetUp):
    def test_home_page(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_todo(self):
        resp = self.app.get('/api/v1/todos')
        self.assertEqual(resp.status_code, 200)


class TestTodoResources(DatabaseSetUp):
    def test_todolist_get(self):
        resp = self.app.get('/api/v1/todos')
        self.assertEqual(resp.status_code, 200)

    def test_todo_get(self):
        self.todo = models.Todo.create(
            name='test todo_1'
        )
        resp = self.app.get('/api/v1/todos/1')
        data = {'id': 1, 'name': 'test todo_1'}
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), data)

    def test_todo_post(self):
        resp = self.app.post('/api/v1/todos',
                             data=json.dumps({'name': 'test todo_1'}),
                             content_type='application/json')
        self.assertEqual(models.Todo.name, 'test todo_1')
        self.assertEqual(models.Todo.id, 1)
        self.assertEqual(resp.status_code, 201)

    def test_todo_put(self):
        self.todo = models.Todo.create(
            name='test todo_1'
        )
        resp = self.app.put(
            '/api/v1/todos/1',
            data=json.dumps({
                'id': '1',
                'name': 'test todo_edit'}),
            content_type='application/json')
        data1 = {'id': 1, 'name': 'test todo_edit'}
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), data1)

    def test_todo_put_not_working(self):
        resp = self.app.put(
            '/api/v1/todos/999',
            data=json.dumps({
                'id': '999',
                'name': 'test todo_999'}),
            content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_todo_delete(self):
        self.todo = models.Todo.create(
            name='test todo_1'
        )
        resp = self.app.delete('/api/v1/todos/1')
        self.assertEqual(resp.status_code, 204)

    def test_todo_delete_not_working(self):
        self.todo = models.Todo.create(
            name='test todo_1'
        )
        resp = self.app.delete('/api/v1/todos/999')
        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()