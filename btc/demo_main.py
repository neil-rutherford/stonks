import demo_funcs
import schedule
import time

def main(window_size=57600, k=2, desired_profit=1.00):
    try:
        # Save BTC price
        demo_funcs.get_btc_price()

        # Load data 
        data = demo_funcs.load_price_data(
            window_size=window_size
        )

        # Use data to generate advice
        advice = demo_funcs.make_advice(
            data=data,
            k=k
        )

        if advice['advice'] == "BUY":
            demo_funcs.buy(advice)
        
        elif advice['advice'] == 'SELL':
            demo_funcs.sell(advice, desired_profit)

        else:
            pass
    
    except ValueError:
        pass

schedule.every().minute.at(":00").do(main)

schedule.every().minute.at(":15").do(demo_funcs.purge)

schedule.every().minute.at(":30").do(main)

schedule.every().minute.at(":45").do(demo_funcs.purge)

while True:
    schedule.run_pending()
    time.sleep(1)
