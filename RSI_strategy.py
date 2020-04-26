import backtrader as bt
import datetime
from collections import defaultdict


# Create a Stratey
class RSI_strategy(bt.Strategy):
    params = (('rsiLowOpen', 30),
              ('rsiHighOpen', 70),
              ('rsiLowClose', 30),
              ('rsiHighClose', 70),
              ('percentage', 0.2),
              ('pentry', 0.015),
              ('stopprofit', 0.9),
              ('stoploss',0.01),
              ('valid', 10),
              ('printAllLogs', False),
              ('printImportantLogs', False),
              )

    def log(self, txt, important=False, data=None):
        if self.p.printAllLogs or (self.p.printImportantLogs and important):
            print(txt)

    def __init__(self):
        # To keep track of pending orders
        self.orefs = dict()

        # Add 3 MovingAverageSimple indicator per stock
        self.rsi = dict()
        self.lowestcash = self.broker.getcash()
        for data in self.datas:
            self.rsi[data] = bt.indicators.RSI(data)

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log("---------------------  "+ trade.getdataname() + "  CLOSING!!  LONG" * trade.long + "  CLOSING!!  SHORT" * (
                not trade.long) + " ---------------------"
                                  '\nGROSS {} \ NET {} \ CASH: {} \ VALUE ASSETS: {} \n\n\n'.format(
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2),
                round(self.broker.getcash(), 2),
                round(self.broker.getvalue(), 2)), important=True)

        elif trade.isopen:
            self.log("--------------------- "+ trade.getdataname() + "  OPENING!! LONG" * trade.long + "  OPENING!! SHORT" * (
                not trade.long) + " ---------------------"
                                  '\nSIZE {} \ PRICE {} \ VALUE: {} \n'.format(trade.size, trade.price, trade.value),
                     important=True)
            print(self.broker.getcash())

    def notify_order(self, order):
        # information about the order

        dt, dn, ref, data = self.datetime.date(), order.data._name, order.ref, order.data

        self.log('{}: Order ref: {} / Type {} / Status {} '.format(self.data.datetime.date(0), ref,
                                                                   'Buy' * order.isbuy() or 'Sell',
                                                                   order.getstatusname()), data=data._name)

        if order.status == order.Submitted:
            return

        if not order.alive():
            price = order.executed.price
            if order.status == order.Completed:
                if order.isbuy():
                    if (order == self.orefs[order.data][1]):
                        self.log("{} -- {} ({}) --> STOP PROFIT ACTIVATED AT PRICE {}".format(dt, dn, ref,
                                                                                            order.executed.price),
                                 data=data._name, important=True)

                        self.setOrders(data, main=None, low=None)

                    elif (order == self.orefs[order.data][2]):
                        self.log("{} -- {} ({})--> STOP LOSS ACTIVATED AT PRICE {}"
                                 .format(dt, dn, ref, price),
                                 data=data._name, important=True)

                        self.setOrders(data, main=None, high=None)

                    else:
                        self.log("{} -- {} ({})--> BUY ESTRATEGICA:  COST {} / PRICE {} / COMMI {}"
                                 .format(dt, dn, ref, order.executed.value, order.executed.price,order.executed.comm),
                                 data=data._name, important=True)

                        self.setOrders(data, main=None)
                        print(order.margin())


                elif order.issell():
                    if (order == self.orefs[order.data][1]):
                        self.log("{} -- {} ({}) --> STOP LOSS ACTIVATED AT PRICE {}"
                                 .format(dt, dn, ref,order.executed.price),
                                 data=data._name,  important=True)
                        self.setOrders(data, main=None, low=None)

                    elif (order == self.orefs[order.data][2]):
                        self.log("{} -- {} ({})--> STOP PROFIT ACTIVATED AT PRICE {}"
                                 .format(dt, dn, ref, price),
                                 data=data._name, important=True)

                        self.setOrders(data, main=None, high=None)

                    else:
                        self.log("{} -- {} ({})--> SELL ESTRATEGICA:  COST {} / PRICE {} / COMMI {}"
                                 .format(dt, dn, ref, order.executed.value,order.executed.price,order.executed.comm),
                                 data=data._name,  important=True)
                        self.setOrders(data, main=None)


            elif order.status == order.Canceled:


                if order.issell():
                    if (self.orefs[data][1] == order):
                        self.log("STOP {} CANCELED".format(ref), data=data._name)

                    elif (self.orefs[data][2] == order):
                        self.log("LIMIT {} CANCELED".format(ref), data=data._name)

                    if (self.orefs[data][1] is None and self.orefs[data][2] is None):
                        self.log("STOP/LIMIT CANCELED".format(ref), data=data._name)
                else:
                    if (self.orefs[data][1] == order):
                        self.log("LIMIT {} CANCELED".format(ref), data=data._name)
                    elif (self.orefs[data][2] == order):
                        self.log("STOP {} CANCELED".format(ref), data=data._name)


                    if (self.orefs[data][1] is None and self.orefs[data][2] is None):
                        self.log("STOP/LIMIT CANCELED".format(ref), data=data._name)

                self.setOrders(data, order=order)


            elif order.status == order.Rejected:
                self.log("ORDER {} REJECTED".format(ref), data=data._name,  important=True)
                #self.setOrders(data, order=order)



            elif order.status == order.Margin:
                self.log("ORDER {} MARGIN CALL from {}".format(ref, dn), important=True)
                #self.setOrders(data, order=order)



            else:
                print(order.getstatusname() + "-----------------ANOTHER THING----------------- \n" * 20)
                if (self.orefs[data][1] == order):
                    self.setOrders(data, low=None)
                elif (self.orefs[data][2] == order):
                    self.setOrders(data, high=None)
                elif (self.orefs[data][0] == order):
                    self.setOrders(data, main=None)

    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):
            # Check if an order is pending ... if yes, we cannot send a 2nd one

            dt, dn, p = self.datetime.date(), d._name, d.close[0]

            budget = self.broker.getcash()
            if(self.lowestcash > budget):
                self.lowestcash = budget
            size = round((budget * self.p.percentage) / p)

            if self.orefs.get(d, [None, None, None])[0] is not None:
                return


            rsi = self.rsi[d]

            # Check if we are in the market
            if not self.getposition(d) and size>0:

                # Not yet ... we MIGHT BUY if ...
                if rsi[0] < self.p.rsiLowOpen:
                    p = p * (1.0 + self.p.pentry)
                    profitPrice = p*(1.0+self.p.stopprofit)
                    valid = datetime.timedelta(self.p.valid)

                    #size = round((budget * self.p.percentage) / p)

                    mainside = self.buy(data=d, limit=p, valid=valid, transmit=False)
                    highside = self.sell(data=d, size=mainside.size, price=profitPrice, exectype=bt.Order.Limit,
                                         transmit=False, parent=mainside)
                    lowside = self.sell(data=d, size=mainside.size, trailpercent=self.p.stoploss, exectype=bt.Order.StopTrail,
                                        transmit=True, parent=mainside)

                    o = [mainside, lowside, highside]


                    self.orefs[d] = [o for o in o]
                    self.log('{} -- {} BUY REQUEST: PRICE {} \ SIZE {}'.format(dt, dn, p, mainside.size ), data=d._name, important=True)

                # elif rsi[0] > self.p.rsiHighOpen and budget>0:
                #     p = p * (1.0 + self.p.pentry)
                #     valid = datetime.timedelta(self.p.valid)
                #
                #     profitPrice = p*(1.0-self.p.stopprofit)
                #
                #     mainside = self.sell(data=d, size=size, limit=p, valid=valid, transmit=False)
                #     lowside = self.buy(data=d,  size=mainside.size, price=profitPrice, exectype=bt.Order.Limit,
                #                        transmit=False, parent=mainside)
                #     highside = self.buy(data=d, size=mainside.size, trailpercent=self.p.stoploss, exectype=bt.Order.StopTrailLimit,
                #                         transmit=True, parent=mainside)
                #
                #     o = [mainside, lowside, highside]
                #
                #     self.orefs[d] = [o for o in o]
                #     self.log('{} -- {} SELL REQUEST: PRICE {} \ SIZE {}'
                #         .format(dt, dn, p, size)
                #         , data=d._name,  important=True)

            else:
                order = self.orefs.get(d, None)
                if order is not None and order[1] is not None:
                    if order[1].issell() and rsi[0] > self.p.rsiHighClose:
                        # SELL, SELL, SELL!!! (with all possible default parameters)
                        self.cancel(self.orefs[d][1])
                        self.cancel(self.orefs[d][2])
                        self.setOrders(d, main=self.sell(data=d, size=self.getposition(d).size))

                        self.log('{}: CLOSE LONG POSITION {} AT PRICE {}'.format(dt, dn, p),
                                 data=d._name,  important=True)

                    elif order[1].isbuy() and rsi[0] < self.p.rsiLowClose:
                        # SELL, SELL, SELL!!! (with all possible default parameters)
                        self.cancel(self.orefs[d][1])
                        self.cancel(self.orefs[d][2])
                        self.setOrders(d, main=self.buy(data=d, size=self.getposition(d).size))

                        self.log('{}: CLOSE SHORT POSITION {} AT PRICE {}'.format(dt, dn, p),
                                 data=d._name, important=True)

    def setOrders(self, data, order=None, **kwargs):


        if (kwargs.get('reset', False) == True):

            self.orefs[data][0] = None
            self.orefs[data][1] = None
            self.orefs[data][2] = None

        elif(order is not None):
            if (self.orefs[data][1] == order):
                self.orefs[data][1] =None
            elif (self.orefs[data][2] == order):
                self.orefs[data][2] =None
            elif (self.orefs[data][0] == order):
                self.orefs[data][0] =None
        else:
            self.orefs[data][0] = kwargs.get('main', self.orefs[data][0])
            self.orefs[data][1] = kwargs.get('low', self.orefs[data][1])
            self.orefs[data][2] = kwargs.get('high', self.orefs[data][2])

    def stop(self):
        print("Money: {}, LO {}, HO {}, LC{} HC {}".format(self.broker.getvalue(), self.p.rsiLowOpen, self.p.rsiHighOpen, self.p.rsiLowClose, self.p.rsiHighClose))
        print("Lowest Cash: {}".format(self.lowestcash))

