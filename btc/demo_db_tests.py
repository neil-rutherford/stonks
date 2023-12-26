import unittest
from demo_db_utils import *
import os

class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        create_database()

    def test_price(self):
        create_price(12345.67)
        create_price(76543.21)
        results = read_prices(20)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 2)
        self.assertEqual(results[0]['price'], 76543.21)
        self.assertEqual(results[1]['id'], 1)
        self.assertEqual(results[1]['price'], 12345.67)

    def test_advice(self):
        create_advice(
            price=5.0,
            sma=10000.0,
            standard_deviation=500.0,
            upper_band=10500.0,
            lower_band=9500.0,
            advice='BUY'
        )
        results = read_last_advice()
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['price'], 5.0)
        self.assertEqual(results[0]['sma'], 10000.0)
        self.assertEqual(results[0]['standard_deviation'], 500.0)
        self.assertEqual(results[0]['upper_band'], 10500.0)
        self.assertEqual(results[0]['lower_band'], 9500.0)
        self.assertEqual(results[0]['advice'], 'BUY')
        create_advice(
            price=12345.67,
            sma=10000.0,
            standard_deviation=500.0,
            upper_band=10500.0,
            lower_band=9500.0,
            advice='SELL'
        )
        results = read_last_advice()
        self.assertEqual(results[0]['id'], 2)
        self.assertEqual(results[0]['price'], 12345.67)
        self.assertEqual(results[0]['sma'], 10000.0)
        self.assertEqual(results[0]['standard_deviation'], 500.0)
        self.assertEqual(results[0]['upper_band'], 10500.0)
        self.assertEqual(results[0]['lower_band'], 9500.0)
        self.assertEqual(results[0]['advice'], 'SELL')

    def test_buy_sell(self):
        results = read_last_trade()
        self.assertEqual(len(results), 0)
        create_buy(
            amount=200.0,
            buy_advice_id=1,
            buy_price=5.0
        )
        results = read_last_trade()
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['amount'], 200.0)
        self.assertEqual(results[0]['buy_advice_id'], 1)
        self.assertEqual(results[0]['buy_price'], 5.0)
        self.assertEqual(results[0]['sell_advice_id'], None)
        self.assertEqual(results[0]['sell_price'], None)
        self.assertEqual(results[0]['profit_multiplier'], None)

        create_sell(
            trade_id=1,
            sell_advice_id=2,
            sell_price=12345.67,
            profit_multiplier=12345.67/5.0
        )
        results = read_last_trade()
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['amount'], 200.0)
        self.assertEqual(results[0]['buy_advice_id'], 1)
        self.assertEqual(results[0]['buy_price'], 5.0)
        self.assertEqual(results[0]['sell_advice_id'], 2)
        self.assertEqual(results[0]['sell_price'], 12345.67)
        self.assertEqual(results[0]['profit_multiplier'], 2469.134)
        
    def test_funds(self):
        results = read_account_balances(1)
        self.assertEqual(len(results), 0)

        create_seed_funds(200.0)
        results = read_account_balances(1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['trade_id'], None)
        self.assertEqual(results[0]['balance'], 200.0)

        update_funds(
            trade_id=1,
            amount=0.0
        )
        results = read_account_balances(1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 2)
        self.assertEqual(results[0]['trade_id'], 1)
        self.assertEqual(results[0]['balance'], 0.0)

        update_funds(
            trade_id=1,
            amount=200*2469.134
        )
        results = read_account_balances(1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 3)
        self.assertEqual(results[0]['trade_id'], 1)
        self.assertEqual(results[0]['balance'], 493826.8)

if __name__ == '__main__':
    unittest.main()
