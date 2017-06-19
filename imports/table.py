import boto3
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamo_db = boto3.resource('dynamodb')


def print_exception(e):
    logger.error(e)


"""
__author__      = Umair Ansari
__copyright__   = Copyright 2007, Cielo WiGle
__date__        = 25, April 2017
__version__     = 1.0.0"""


class Table:
    def __init__(self, table_name):
        """
        @Author: umair
        :param table_name: 
        """
        try:
            self.table = dynamo_db.Table(table_name)
        except Exception as e:
            print_exception(e)
            self.table = None

    def get_item_by_key(self, key):
        """
        @Author: umair
        :param key: 
        :return: 
        """
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item", None)
        except Exception as e:
            print_exception(e)
            return None

    def delete_item_by_key(self, key, return_values):
        """
        @Author: umair
        :param key: 
        :param return_values: 
        :return: 
        """
        try:
            response = self.table.delete_item(Key=key, ReturnValues=return_values)
            if 'Attributes' in response:
                return response
            else:
                return None
        except Exception as e:
            print_exception(e)
            return None

    def put_item(self, item):
        """
        @Author: umair
        :param item: item is the json you wants to insert into the table
        :return: return None is success, Exception stack trace
        """
        try:
            self.table.put_item(Item=item)
            return None
        except Exception as e:
            print_exception(e)
            return e

    def get_table_object(self):
        """
        @Author: umair
        :return: 
        """
        return self.table

    def update_item_by_key(self, key, update_expression, expression_attribute_values, return_values, condition_expression=None):
        """
        @Author: umair
        :param key: 
        :param update_expression: 
        :param expression_attribute_values: 
        :param return_values: 
        :param condition_expression: 
        :return: 
        """
        try:
            if condition_expression is None:
                response = self.table.update_item(Key=key,
                                                  UpdateExpression=update_expression,
                                                  ExpressionAttributeValues=expression_attribute_values,
                                                  ReturnValues=return_values)
            else:
                response = self.table.update_item(Key=key,
                                                  ConditionExpression=condition_expression,
                                                  UpdateExpression=update_expression,
                                                  ExpressionAttributeValues=expression_attribute_values,
                                                  ReturnValues=return_values)

            if 'Attributes' in response:
                return response
            else:
                return None
        except Exception as e:
            print_exception(e)
            return None

    def get_item_via_query(self, key_expression, index=None, filter_expression=None):
        """
        @Author: umair
        :param filter_expression: 
        :param key_expression: 
        :param index: 
        :param response_count: 
        :param item: 
        :return: 
        """
        try:
            if index is None:
                response = self.table.query(KeyConditionExpression=key_expression)
            elif index is not None and filter_expression is None:
                response = self.table.query(IndexName=index, KeyConditionExpression=key_expression)
            elif filter_expression is not None and index is None:
                response = self.table.query(KeyConditionExpression=key_expression, FilterExpression=filter_expression)
            else:
                response = self.table.query(IndexName=index, KeyConditionExpression=key_expression, FilterExpression=filter_expression)

            if response["Count"] > 0:
                return response.get("Items", None)
            return None
        except Exception as e:
            print_exception(e)
            return None

    def get_item_via_query_count(self, key_expression, index=None, filter_expression=None):
        """
        @Author: umair
        :param filter_expression: 
        :param key_expression: 
        :param index: 
        :return: 
        """
        try:
            if index is None:
                response = self.table.query(KeyConditionExpression=key_expression)
            elif index is not None and filter_expression is None:
                response = self.table.query(IndexName=index, KeyConditionExpression=key_expression)
            elif filter_expression is not None and index is None:
                response = self.table.query(KeyConditionExpression=key_expression, FilterExpression=filter_expression)
            else:
                response = self.table.query(IndexName=index, KeyConditionExpression=key_expression, FilterExpression=filter_expression)
            return response.get("Count", 0)
        except Exception as e:
            print_exception(e)
            return None

    def get_via_query(self, key_expression, index=None, filter_expression=None):
        """
        @Author: umair
        :param filter_expression: 
        :param key_expression: 
        :param index: 
        :return: 
        """
        try:
            if index is None:
                return self.table.query(KeyConditionExpression=key_expression)
            elif index is not None and filter_expression is None:
                return self.table.query(IndexName=index, KeyConditionExpression=key_expression)
            elif filter_expression is not None and index is None:
                return self.table.query(KeyConditionExpression=key_expression, FilterExpression=filter_expression)
            else:
                return self.table.query(IndexName=index, KeyConditionExpression=key_expression, FilterExpression=filter_expression)

        except Exception as e:
            print_exception(e)
            return None

    def scan_table(self):
        """
        Scans a table and returns the list of Items
        params: table name
        return: list
        """
        list_item = []
        result_set = self.table.scan()

        for item in result_set['Items']:
            list_item.append(item)
        while 'LastEvaluatedKey' in result_set:
            result_set = self.table.scan(
                ExclusiveStartKey=result_set['LastEvaluatedKey']
            )
            for item in result_set['Items']:
                list_item.append(item)
        return list_item
