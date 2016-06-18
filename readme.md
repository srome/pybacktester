# PyBacktester

An event-based backtester written in Python. The backtester is built with a consumer/producer pattern where
the consumer is the Controller class and the producer is the DataSource class. The trading algorithm is contained
in the Algorithm class.

## Custom Portfolio
A custom portfolio may be created by instantiating the Portfolio class and adding stocks, prices, and shares. This
is demonstrated in the many of the unit tests in the tests.py file.

## Algorithmic Trading Interface
The "Algorithm" class defines a strategy that the backtester uses. To make your own, you must implement
a "generate_orders" method. An example algorithm is included in the base class.

## Alternative DataSource
The basic DataSource included is built on top of pandas DataReader. This source may be modified to be any realtime
data feed. The DataSource's single requirement is to fill a Queue class with data from the feed. The data should be
in the form of a tuple (Timestamp/Id, Ticker str, Price float).

## Run
Enter "python backtester.py" for a default run. Output is logged to run.log.

# Disclaimer
This code is meant for educational purposes only. The included algorithm should NOT be used to
inform real trades in any way. In fact, it randomly liquidates positions.