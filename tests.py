import unittest

from backtester import Controller
from domain import Portfolio

class ComponentTests(unittest.TestCase):

    def test_stream(self):
        import datetime
        from multiprocessing import Queue

        p = Portfolio(balance=10.0)
        p.update(ticker='TICK', price=9.0)
        p.set_shares('TICK', 3.0)

        cur_time = lambda : datetime.datetime.now().strftime('%Y-%m-%d')
        q = Queue()
        q.put((cur_time(), 'TICK', 10.0))
        q.put((cur_time(), 'TICK', 11.0))
        q.put((cur_time(), 'TICK', 12.0))
        q.put('POISON') #Stops simulation

        c = Controller(portfolio=p)

        Controller.backtest(q, controller=c) # Run backtest is the local version

        self.assertAlmostEqual(p.get_total_value(), 10.+3.*12., delta=1e-7)
        self.assertAlmostEqual(p.get_price('TICK'), 12., delta=1e-7)

    def test_update(self):
        p = Portfolio(balance=10.0)
        p.update(ticker='TICK', price=10.0)
        p.set_shares('TICK', 3.0)
        eps = 1e-7

        self.assertTrue(abs(10.0 - p.balance) < eps)  # Balance correct
        self.assertTrue(abs(3.0 - p.get_shares('TICK'))<eps) # Shares updated
        self.assertTrue(abs(40.0 - p.get_total_value()) < eps)  # Shares updated

    def test_buy(self):
        p = Portfolio(balance=33.0)
        p.update(ticker='TICK', price=12.3)
        p.set_shares('TICK', 3.0)
        cont = Controller(p)
        success = cont.process_receipt(('TICK',11.0, 2.0, 10.0))
        eps = 1e-4

        self.assertTrue(success) # Trade went through
        self.assertTrue(abs(1.0-p.balance)<eps) # Balance updated correctly
        self.assertTrue(abs(5.0 - p.get_shares('TICK'))<eps) # Shares updated

    def test_buy_fail(self):
        p = Portfolio(balance=13.0)
        p.update(ticker='TICK', price=12.3)
        p.set_shares('TICK', 3.0)
        cont = Controller(p)
        success = cont.process_receipt(('TICK',11.0, 2.0, 10.0))

        self.assertFalse(success) # Trade failed

    def test_sell(self):
        p = Portfolio(balance=13.0)
        p.update(ticker='TICK', price=12.3)
        p.set_shares('TICK', 3.0)
        cont = Controller(p)
        success = cont.process_receipt(('TICK', 11.0, -2.0, 10.0))
        eps=1e-4

        self.assertTrue(success) # Trade went through
        self.assertTrue(abs(25.0-p.balance)<eps) # Balance updated correctly
        self.assertTrue(abs(1.0 - p.get_shares('TICK'))<eps) # Shares updated


    def test_liquidate(self):
        p = Portfolio(balance=13.0)
        p.update(ticker='TICK', price=12.3)
        p.set_shares('TICK', 3.0)
        cont = Controller(p)
        success = cont.process_receipt(('TICK', 11.0, -5.0, 10.0))
        eps = 1e-4

        updated_fee = cont._order_api._calculate_fee(11.0*3.0)

        self.assertTrue(success)  # Trade went through
        self.assertTrue(abs(13.0 + (3*11.0) - updated_fee - p.balance) < eps)  # Balance updated correctly
        self.assertTrue(abs(0.0 - p.get_shares('TICK')) < eps)  # Shares updated
        self.assertTrue(abs(12.3 - p.get_price('TICK')) < eps)  # Price not updated from slippage

if __name__ == '__main__':
    unittest.main()
