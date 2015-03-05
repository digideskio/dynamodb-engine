"""
Testing the Model
"""
import unittest

from .attributes import StringAttribute
from .exceptions import MissingHashKeyError
from .models import Model

DYNAMODB_HOST = 'localhost'
DYNAMODB_PORT = 8000


class User(Model):
    """ Basic User model used for testing purposes """
    class Meta:
        table_name = 'users'
        dynamodb_local = {
            'host': DYNAMODB_HOST,
            'port': DYNAMODB_PORT
        }
        throughput = {
            'read': 22,
            'write': 18
        }

    email = StringAttribute('email', hash_key=True)
    first_name = StringAttribute('firstName')
    last_name = StringAttribute('lastName')


class TestModel(unittest.TestCase):
    """
    Unit tests for the model
    """
    def setUp(self):
        """ Set up method """
        self.user = User()
        self.user.email = 'sebastian.dahlgren@skymill.se'
        self.user.first_name = 'Sebastian'
        self.user.last_name = 'Dahlgren'
        self.user.create_table()
        self.user.save()

    def tearDown(self):
        """ Tear down method """
        self.user.delete_table()

    def test_create_table_name(self):
        """
        Ensure that tables get the right name
        """
        self.assertEqual(
            self.user.describe_table()['Table']['TableName'],
            'users')

    def test_create_table_throughput(self):
        """
        Ensure that the throughput is provisioned properly
        """
        cus = self.user.describe_table()['Table']['ProvisionedThroughput']
        self.assertEqual(cus['ReadCapacityUnits'], 22)
        self.assertEqual(cus['WriteCapacityUnits'], 18)

    def test_create_table_hash(self):
        """
        Test that a basic table can be created. Only hash key
        """
        class Test(Model):
            class Meta:
                table_name = 'test'
                dynamodb_local = {
                    'host': DYNAMODB_HOST,
                    'port': DYNAMODB_PORT
                }

            username = StringAttribute('username', hash_key=True)

        test = Test()
        test.username = 'myuser'
        test.create_table()
        key_schema = test.describe_table()['Table']['KeySchema']

        self.assertEqual(len(key_schema), 1)
        self.assertEqual(key_schema[0]['KeyType'], 'HASH')
        self.assertEqual(key_schema[0]['AttributeName'], 'username')

        test.delete_table()

    def test_create_table_hash_range(self):
        """
        Test that a basic table can be created. Both hash key and range key
        """
        class Test(Model):
            class Meta:
                table_name = 'test'
                dynamodb_local = {
                    'host': DYNAMODB_HOST,
                    'port': DYNAMODB_PORT
                }

            username = StringAttribute('username', hash_key=True)
            post = StringAttribute('post', range_key=True)

        test = Test()
        test.username = 'myuser'
        test.post = 'example'
        test.create_table()
        key_schemas = test.describe_table()['Table']['KeySchema']

        self.assertEqual(len(key_schemas), 2)
        for key_schema in key_schemas:
            if key_schema['KeyType'] == 'HASH':
                self.assertEqual(key_schema['AttributeName'], 'username')
            if key_schema['KeyType'] == 'RANGE':
                self.assertEqual(key_schema['AttributeName'], 'post')

        test.delete_table()

    def test_missing_hash_key(self):
        """
        Check if a missing hash key raises an exception
        """
        class User(Model):
            class Meta:
                table_name = 'test'
                dynamodb_local = {
                    'host': DYNAMODB_HOST,
                    'port': DYNAMODB_PORT
                }

            first_name = StringAttribute('firstName')
            last_name = StringAttribute('lastName')

        user = User()
        self.assertRaises(MissingHashKeyError, user.create_table)


if __name__ == '__main__':
    unittest.main()
