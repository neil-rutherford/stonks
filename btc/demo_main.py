import demo_funcs
import sys

def main(window_size=20, k=1, desired_profit=1.01):
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
            buy(advice)
        
        elif advice['advice'] == 'SELL':
            sell(advice, desired_profit)

        else:
            pass
    
    except ValueError:
        pass

if __name__ == '__main__':
    main()
