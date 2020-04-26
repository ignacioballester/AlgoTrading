import backtrader as bt
import datetime
from collections import defaultdict


# Create a Stratey
class TestStrategy(bt.Strategy):
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
        if self.p.printlog:
            print(txt)
            if space:
                print()

    def __init__(self):
        # To keep track of pending orders
        print("start")
        self.lowestcash = self.broker.getcash()
        # Add 3 MovingAverageSimple indicator per stoc

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
                   print("buy")
                   print(order.executed.price)

                elif order.issell():
                   print("seññ")
                   print(order.executed.price)



            elif order.status == order.Canceled:
                print("canceled")

            elif order.status == order.Rejected:
                print("rejected")


            elif order.status == order.Margin:
                print(order.data.close[0])
                self.log("ORDER {} MARGIN CALL".format(ref))
                print("AVAILABLE CASH: {} {}".format(self.broker.getcash(), self.broker.getvalue()))

            else:
                print(order.getstatusname() + "-----------------ANOTHER THING----------------- \n" * 20)
                self.setOrders(data, reset=True)



    def next(self):

        # Simply log the closing price of the series from the reference
        budget = self.broker.getcash()
        if (self.lowestcash > budget):
            self.lowestcash = budget

        if self.datetime.date() == datetime.date(2018, 2, 27):
            self.sell()
            print("buy")

        elif self.datetime.date() == datetime.date(2018, 9, 18):
            self.close()
        if budget<0:
            self.close()

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(
                "---------------------  " + trade.getdataname() + "  CLOSING!!  LONG" * trade.long + "  CLOSING!!  SHORT" * (not trade.long) + " ---------------------"
                                      '\nGROSS {} \ NET {} \ CASH: {} \ VALUE ASSETS: {} \n\n\n'.format(
                    round(trade.pnl, 2),
                    round(trade.pnlcomm, 2),
                    round(self.broker.getcash(), 2),
                    round(self.broker.getvalue(), 2)))
            print(self.lowestcash)

        elif trade.isopen:
            self.log(
                "--------------------- " + trade.getdataname() + "  OPENING!! LONG" * trade.long + "  OPENING!! SHORT" * (
                    not trade.long) + " ---------------------"
                                      '\nSIZE {} \ PRICE {} \ VALUE: {} \CASH {} \n'.format(trade.size, trade.price, trade.value, self.broker.getcash()))
            print(self.broker.getcash())