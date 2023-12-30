import requests
import demo_db_utils as db_utils
import datetime
import numpy as np

def logger(message):
    with open('errors.log', 'a') as f:
        f.write(f"{message}\n")


def get_btc_price():
    r = requests.get('https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT')
    if r.status_code == 200:
        db_utils.create_price(float(r.json()['price']))
        return float(r.json()['price'])
    else:
        logger(f"[get_btc_price] Failed at {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}. Error message: {r.json()}")
        raise ValueError("Failed to get BTC price from API.")


def load_price_data(window_size):
    price_data = db_utils.read_prices(window_size)
    data_list = []
    if len(price_data) == window_size:
        for x in price_data:
            data_list.append(x['price'])
        return data_list
    else:
        #logger("[load_price_data] Insufficient data.")
        raise ValueError("Insufficient data.")


def get_sma(data):
    return (sum(data) / len(data))


def get_bsh(price, upper_band, lower_band):
    if float(price) <= float(lower_band):
        return "BUY"
    elif float(price) >= float(upper_band):
        return "SELL"
    else:
        return "HOLD"


def make_advice(data, k=2):
    sma = get_sma(data)
    standard_deviation = np.std(data)
    data_dict = {
        'price': data[0],
        'sma': sma,
        'standard_deviation': standard_deviation,
        'upper_band': sma + (standard_deviation * k),
        'lower_band': sma - (standard_deviation * k)
    }
    advice=get_bsh(
        price=data_dict['price'],
        upper_band=data_dict['upper_band'],
        lower_band=data_dict['lower_band']
    )
    data_dict['advice'] = advice
    db_utils.create_advice(
        price=data_dict['price'],
        sma=data_dict['sma'],
        standard_deviation=data_dict['standard_deviation'],
        upper_band=data_dict['upper_band'],
        lower_band=data_dict['lower_band'],
        advice=data_dict['advice']
    )
    return db_utils.read_last_advice()[0]


def buy(buy_advice_dict):
    funds = db_utils.read_account_balances(1)
    print(f"FUnds: {funds}")

    #if len(funds) == 0:
        #logger("[buy] Run `create_seed_funds()` function! No money in the account.")
        #pass

    if len(funds) == 0 or funds[0]['balance'] == 0.0:
        print("I'm not gonna buy anything!")
        pass
    else:
        last_trade = db_utils.read_last_trade()
        if len(last_trade) == 1:
            if not last_trade[0]['sell_advice_id']:
                pass

        db_utils.create_buy(
            amount=funds[0]['balance'] * 0.999, # Simulate Binance 0.1% fee
            buy_advice_id=buy_advice_dict['id'],
            buy_price=buy_advice_dict['price']
        )

        last_trade = db_utils.read_last_trade()
        db_utils.update_funds(
            trade_id=last_trade[0]['id'],
            amount=0.0
        )
        return last_trade


def sell(sell_advice_dict, desired_profit):
    # If there are no entries in the transaction log, pass
    last_trade = db_utils.read_last_trade()
    if len(last_trade) == 0 or last_trade[0]['sell_advice_id']:
        pass
    else:
        # If the proposed sale price is less than or equal to buy price, pass
        profit_multiplier = (float(sell_advice_dict['price']) / float(last_trade[0]['buy_price']))
        if profit_multiplier < float(desired_profit):
            pass
        else:
            # Update trade
            db_utils.create_sell(
                trade_id=last_trade[0]['id'],
                sell_advice_id=sell_advice_dict['id'],
                sell_price=sell_advice_dict['price'],
                profit_multiplier=profit_multiplier
            )
            # Update funds
            last_trade = db_utils.read_last_trade()
            db_utils.update_funds(
                trade_id=last_trade[0]['id'],
                amount=((profit_multiplier) * (last_trade[0]['amount'])) * 0.999 # Simulate Binance 0.1% fee
            )
            return last_trade


def purge(older_than=528):
    db_utils.purge_old_prices(older_than)
    db_utils.purge_old_advices(older_than)
