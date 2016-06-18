import numpy as np

class Algorithm:
    '''
    Example algorithm for trading. Must implement a "generate_orders" function which returns a list of orders.
    Each order is a tuple of the form
        ( Stock Ticker str, Current Price float, Order Amount in shares float)

    Algorithm trades for stocks via a rolling window strategy, and randomly liquidates positions
    '''
    def __init__(self):
        self._averages = {}
        self._lambda = .5
        self._fee_estimate = lambda x : x*.04+10
        self._updates = 0
        self._price_window = 20
        self._trend = np.zeros(self._price_window)
        self._minimum_wait_between_trades = 5 # Must be less than price window
        self._last_trade = 0
        self._last_date = None

    def add_stock(self, stock, price):
        self._averages[stock] = price

    def _determine_if_trading(self, date, portfolio_value, cash_balance):
        time_delay_met = True
        trade = False
        override = False
        self._updates += 1

        if self._last_date is not None:
            if (date - self._last_date).days <= self._minimum_wait_between_trades:
                # Make orders based on previous day
                return False

        if self._updates == self._price_window+1:
            trade = True

        if (np.mean(self._trend)-portfolio_value)/portfolio_value > 0.05:
            override = True

        if cash_balance > portfolio_value*.03:
            override = True

        return trade or override

    def generate_orders(self, timestamp, portfolio):
        orders = []
        cash_balance = portfolio.balance
        portfolio_value = portfolio.get_total_value()
        self.add_trend_value(portfolio_value)

        if not self._determine_if_trading(timestamp,portfolio_value,cash_balance):
            return orders

        valid_stocks = [stock for stock in self._averages if portfolio.get_update_count(stock) > self._price_window]

        if len(valid_stocks) == 0:
            return orders

        for stock in np.random.choice(valid_stocks, replace=False, size=len(valid_stocks)):
            amt = cash_balance / len(valid_stocks) # Spend available cash
            relative_change = (self.get_window_average(stock=stock) - self.get_price(stock))/self.get_price(stock)

            if abs(relative_change) > .03:
                # Positive is buy, negative is sell
                order_type = np.sign(relative_change)
                if order_type > 0 and np.random.uniform(0,1,size=1)[0] < .9:
                    amt = np.round(amt/self.get_price(stock),0)
                else:
                    amt = - portfolio.get_shares(stock) # Liquidate! Why not?

                if abs(amt) < .01:
                    # Stop small trades
                    continue

                orders.append((stock, self.get_price(stock), amt))

        self._last_trade = self._updates
        self._last_date = timestamp

        return orders

    def get_window_average(self, stock):
        return np.mean(self._averages[stock]['History'])

    def update(self, stock, price):
        if stock in self._averages:
            self.add_price(stock, price)
        else:
            length = self._price_window
            self._averages[stock] = {'History' : np.zeros(length), 'Index' : 0, 'Length' : length}
            data = self._averages[stock]['History']
            data[0] = price

    def get_price(self, stock):
        # Assumes history is full
        return self._averages[stock]['History'][-1]

    def add_price(self, stock, price):
        history = self._averages[stock]['History']
        ind = self._averages[stock]['Index']
        length = self._averages[stock]['Length']
        if ind < length-1:
            history[ind+1] = price
            self._averages[stock]['Index'] = ind + 1
        elif ind == length-1:
            history[:-1] = history[1:]
            history[-1] = price

    def add_trend_value(self, value):
        history = self._trend
        if self._updates <= self._price_window - 1:
            history[self._updates] = value
        elif self._updates > self._price_window-1:
            history[:-1] = history[1:]
            history[-1] = value