import time
import unittest
import random
from csvstore import CSVBotStroe

class TestCSVBotStore(unittest.TestCase):

    def get_test_order(self,param:dict = {}):
        """Для генерации тестовых заказов"""

        raw_order = \
        {
            "web": False,
            "time_in_force": "good_til_cancelled",
            "replaced": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 58757.5,
            "post_only": False,
            "order_type": "limit",
            "order_state": "reject",
            "order_id": f'test-{time.time()}',
            "max_show": 12.0,
            "last_update_timestamp": int(time.time()),
            "label": "test",
            "is_liquidation": False,
            "instrument_name": "BTC-PERPETUAL",
            "filled_amount": 0.0,
            "direction": "buy",
            "creation_timestamp": int(time.time()),
            "commission": 0.0,
            "average_price": 0.0,
            "api": True,
            "amount": 1
        }

        return {**raw_order, **param}

    @classmethod
    def setUpClass(self):
        self.store= CSVBotStroe(
            './test.csv', 
            save_param = { 'decimal' : ',' }, 
            decimal = ','
        )


    def test_query_with_param(self):
        """Проверяем правильность выборок по параметрам. В тестовом файле 3 заказа \
        с ID = ETH-1176857086 , 5581294030 , 5580894452 с параметрами active = 1 \
        state in (open,filled)
        """

        orders = self.store.get(
            param = { 'active' : 1 , 'state': ['open','filled'] }, 
            order_by = { 'real_create' : 'desc' }
        )

        self.assertIs(type(orders),list,'Ожидается список ордеров')

        check_id = dict.fromkeys(
            ['ETH-1176857086', '5581294030', '5580894452'],
            0
        )

        for order in orders:
            if order['id'] in check_id:
                check_id[order['id']] = 1

        self.assertEqual(sum(check_id.values()),3,'Не найдены заказы удовлетворяющие условия')


    def test_query_with_id(self):
        """Проверяем правильность выборок по ID. В тестовом файле есть ордер с ID = 5537502131"""

        order = self.store.get(id = '5537502131')

        self.assertNotEqual(order,None,'Ожидается ордер с типом dict')


    def test_insert(self):
        """Проверяем добавление нового ордера базу. Со стандартным набором параметров
        """
        
        order = self.get_test_order()
        res_order =  self.store.insert(order)
        self.assertEqual(res_order,None,'Ожидается None результат')


    def test_insert_with_active(self):
        """Проверяем добавление нового ордера базу. 
        Случай, когда новый ордер будет c active = 1
        """
        
        order = self.get_test_order()
        res_order =  self.store.insert(order, return_is_active=False)
        self.assertNotEqual(res_order,None,'Ожидается ордер с типом dict')


    def test_update(self):
        """Проверяем обновление нового заказа с ID = 5536748587"""

        order = self.get_test_order({'price' : random.randint(50000,60000) })
        res_order =  self.store.update(id = '5536748587',order = order,return_is_active = False)
        self.assertNotEqual(res_order,None,'Ожидается ордер с типом dict')


def main():
    unittest.main()