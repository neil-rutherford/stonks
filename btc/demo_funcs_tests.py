import unittest
from demo_funcs import *
from demo_db_utils import *

class DemoFuncsTestCase(unittest.TestCase):
    def setUp(self):
        create_database()
    
    def test_get_btc_price(self):
        result = get_btc_price()
        self.assertEqual(type(result), float)

    def test_load_price_data(self):
        result = load_price_data(window_size=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(type(result[0]), float)
        
        with self.assertRaises(ValueError):
            result = load_price_data(window_size=20)

    def test_logger(self):
        with open('errors.log', 'r') as f:
            self.assertEqual(f.readlines()[0], '[load_price_data] Insufficient data.\n')

    def test_get_sma(self):
        result = get_sma(data=[1,2,3,4,5,6,7,8,9,10])
        self.assertEqual(result, 5.5)

    def test_get_bsh(self):
        result = get_bsh(
            price=10,
            lower_band=9,
            upper_band=11
        )
        self.assertEqual(result, "HOLD")

        result = get_bsh(
            price=10,
            lower_band=8,
            upper_band=10
        )
        self.assertEqual(result, "SELL")

        result = get_bsh(
            price=10,
            lower_band=11,
            upper_band=16
        )
        self.assertEqual(result, "BUY")

    def test_make_advice(self):
        
        result = make_advice(
            data=[1.,2.,3.,4.,5.,6.,7.,8.,9.,10.],
            k=1
        )
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['price'], 1.0)
        self.assertEqual(result['sma'], 5.5)
        self.assertAlmostEqual(result['standard_deviation'], 2.8722813)
        self.assertAlmostEqual(result['upper_band'], 8.3722813)
        self.assertAlmostEqual(result['lower_band'], 2.6277187)
        self.assertEqual(result['advice'], "BUY")

        result = make_advice(
            data=[10.,9.,8.,7.,6.,5.,4.,3.,2.,1.],
            k=1
        )
        self.assertEqual(result['id'], 2)
        self.assertEqual(result['price'], 10.0)
        self.assertEqual(result['sma'], 5.5)
        self.assertAlmostEqual(result['standard_deviation'], 2.8722813)
        self.assertAlmostEqual(result['upper_band'], 8.3722813)
        self.assertAlmostEqual(result['lower_band'], 2.6277187)
        self.assertEqual(result['advice'], "SELL")

    def test_buy(self):
        
        buy_advice_dict = {
            'id': 1,
            'price': 1.0,
            'sma': 5.5,
            'standard_deviation': 2.8722813,
            'upper_band': 8.3722813,
            'lower_band': 2.6277187,
            'advice': "BUY"
        }
        
        # Check that buy executes
        create_seed_funds(200.0)
        
        result = buy(buy_advice_dict)
        #db = read_last_trade()[0]
        #print(db)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['amount'], 199.8)
        self.assertEqual(result[0]['buy_advice_id'], 1)
        self.assertEqual(result[0]['buy_price'], 1.0)
        self.assertEqual(result[0]['sell_advice_id'], None)
        self.assertEqual(result[0]['sell_price'], None)
        self.assertEqual(result[0]['profit_multiplier'], None)
        funds = read_account_balances(1)
        self.assertEqual(funds[0]['id'], 2)
        self.assertEqual(funds[0]['trade_id'], 1)
        self.assertEqual(funds[0]['balance'], 0.0)

        # Check that logic holds and buy doesn't execute
        buy(buy_advice_dict)
        result = read_last_trade()
        print(result)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['amount'], 199.8)
        self.assertEqual(result[0]['buy_advice_id'], 1)
        self.assertEqual(result[0]['buy_price'], 1.0)
        funds = read_account_balances(1)
        self.assertEqual(funds[0]['id'], 2)
        self.assertEqual(funds[0]['trade_id'], 1)
        self.assertEqual(funds[0]['balance'], 0.0)

    def test_sell(self):
        sell_advice = read_last_advice()[0]
        result = sell(sell_advice, 1.05)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['amount'], 199.8)
        self.assertEqual(result[0]['buy_advice_id'], 1)
        self.assertEqual(result[0]['buy_price'], 1.0)
        self.assertEqual(result[0]['sell_advice_id'], 2)
        self.assertEqual(result[0]['sell_price'], 10.0)
        self.assertEqual(result[0]['profit_multiplier'], 10.0)
        funds = read_account_balances(1)
        self.assertEqual(funds[0]['id'], 3)
        self.assertEqual(funds[0]['trade_id'], 1)
        self.assertEqual(funds[0]['balance'], 1996.002)


if __name__ == '__main__':
    unittest.main()
