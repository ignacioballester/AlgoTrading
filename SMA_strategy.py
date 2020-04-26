import backtrader as bt
import datetime
from collections import defaultdict


# Create a Stratey
class SMA_strategy(bt.Strategy):
    params = dict(
        percentage=0.3,
        maperiods=[14, 50, 200],
        pentry=0.015,
        stopprofit=10,
        stoploss=0.9999,
        valid=10,
        printlog=True
    )

    def log(self, txt, doprint=True, space=False, data=None):
        if self.p.printlog and doprint:
            print(txt)
            if space:
                print()

    def __init__(self):
        # To keep track of pending orders
        self.orefs = dict()

        # Add 3 MovingAverageSimple indicator per stock
        self.sma = dict()
        for data in self.datas:
            sma1 = bt.indicators.SimpleMovingAverage(
                data, period=self.p.maperiods[0])

            sma2 = bt.indicators.SimpleMovingAverage(
                data, period=self.p.maperiods[1])

            sma3 = bt.indicators.SimpleMovingAverage(
                data, period=self.p.maperiods[2])
            self.sma[data] = (sma1, sma2, sma3)

    def notify_order(self, order):
        #information about the order
        dt, dn, ref, data = self.datetime.date(), order.data._name, order.ref, order.data

        self.log('{}: Order ref: {} / Type {} / Status {} '.format(self.data.datetime.date(0),ref, 'Buy' * order.isbuy() or 'Sell',order.getstatusname()), doprint=False, data=data._name)

        if order.status == order.Submitted:
            return

        if not order.alive():
            price = order.executed.price
            if order.status == order.Completed:
                if order.isbuy():
                    self.log("{} -- {} ({}) --> BUY EXECUTED AT PRICE: {}".format(dt, dn, ref, price), data=data._name)
                    self.setOrders(data, main=None)

                elif order.issell():
                    if (order == self.orefs[order.data][1]):
                        self.log("{} -- {} ({}) --> STOP LOSS ACTIVATED AT PRICE {}".format(dt, dn, ref, price), data=data._name)
                        self.setOrders(data, main=None, low=None)

                    elif (order == self.orefs[order.data][2]):
                        self.log("{} -- {} ({})--> STOP PROFIT ACTIVATED AT PRICE {}".format(dt, dn, ref, price),
                                 data=data._name)
                        self.setOrders(data, main=None, high=None)

                    else:
                        self.log("{} -- {} ({})--> SELL ESTRATEGICA AT PRICE {}".format(dt, dn, ref, price),
                                 data=data._name)
                        self.setOrders(data, main=None)

                self.log("", data=data._name)

            elif order.status == order.Canceled:
                if (self.orefs[data][1] == order):
                    self.setOrders(data, low=None)
                    self.log("STOP {} CANCELED".format(ref), data=data._name, doprint=False)

                elif (self.orefs[data][2] == order):
                    self.setOrders(data, high=None)
                    self.log("LIMIT {} CANCELED".format(ref), data=data._name, doprint=False)

                if (self.orefs[data][1] is None and self.orefs[data][2] is None):
                    self.log("STOP/LIMIT CANCELED".format(ref), data=data._name)

            elif order.status == order.Rejected:
                self.log("ORDER {} REJECTED".format(ref), data=data._name)
                self.setOrders(data, reset=True)
                print()

            elif order.status == order.Margin:
                self.log("ORDER {} MARGIN CALL".format(ref))

            else:
                print(order.getstatusname()+ "-----------------ANOTHER THING----------------- \n" * 20)
                self.setOrders(data, reset=True)

    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):

            # Check if an order is pending ... if yes, we cannot send a 2nd one

            dt, dn, p = self.datetime.date(), d._name, d.close[0]

            budget = self.broker.getcash()

            if self.orefs.get(d, [None, None, None])[0] is not None:
                return

            sma3 = self.sma[d][2]
            sma2 = self.sma[d][1]
            sma1 = self.sma[d][0]

            # Check if we are in the market
            if not self.getposition(d):
                # Not yet ... we MIGHT BUY if ...
                if sma3 < sma2 < sma1:
                    p = p * (1.0 + self.p.pentry)
                    pstp = p * (1.0 - self.p.stoploss)
                    plmt = p * (1.0 + self.p.stopprofit)
                    valid = datetime.timedelta(self.p.valid)

                    size = (budget*self.p.percentage)/p

                    mainside = self.buy(data=d, limit=p, valid=valid, transmit=False)
                    lowside = self.sell(data=d, price=pstp, size=mainside.size, exectype=bt.Order.Stop,
                                        transmit=False, parent=mainside)
                    highside = self.sell(data=d, price=plmt, size=mainside.size, exectype=bt.Order.Limit,
                                         transmit=True, parent=mainside)
                    o = [mainside, lowside, highside]

                    self.orefs[d] = [o for o in o]
                    self.log('{} -- {} BUY REQUEST  AT PRICE {}'.format(dt, dn, p), data=d._name)
            else:
                if sma3 > sma2 > sma1:  # and (self.orefs.get(d, [None, None, None][1]) is not None):
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.cancel(self.orefs[d][1])
                    self.cancel(self.orefs[d][2])
                    self.setOrders(d, main=self.sell(data=d, size=self.getposition(d).size))

                    self.log('{}: SELL REQUEST {} AT PRICE {}'.format(dt, dn, p), data=d._name)

    def setOrders(self, data, **kwargs):
        if (kwargs.get('reset', False) == True):
            self.orefs[data][0] = None
            self.orefs[data][1] = None
            self.orefs[data][2] = None
        else:
            self.orefs[data][0] = kwargs.get('main', self.orefs[data][0])
            self.orefs[data][1] = kwargs.get('low', self.orefs[data][1])
            self.orefs[data][2] = kwargs.get('high', self.orefs[data][2])


