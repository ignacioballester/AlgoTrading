import backtrader as bt
import datetime
from tabulate import tabulate


# Create a Strategy
class StrategyTemplate(bt.Strategy):

    def log(self, txt, important=False, data=None):
        if self.p.printAllLogs or (self.p.printImportantLogs and important):
            print(txt)

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log("-"*20 + " " +trade.getdataname() + " CLOSING!!  (LONG) "*trade.long + " CLOSING!!  (SHORT) " * (not trade.long) + "-"*20
                                      +'\nPRICE {} \ GROSS {} \ NET {} \ CASH: {} \ VALUE ASSETS: {} \n\n\n'.format(
                    trade.price,
                    round(trade.pnl, 2),
                    round(trade.pnlcomm, 2),
                    round(self.broker.getcash(), 2),
                    round(self.broker.getvalue(), 2)), important=True)
            if (not trade.long):
                self.p.shortingbudget += abs(trade.value)
                if(self.shortingbudget > self.p.shortingbudget):
                    self.shortingbudget = self.p.shortingbudget

        elif trade.isopen:
            self.log(
                "-"*20 + " " +trade.getdataname() + " OPENING!! (LONG) " * trade.long + "  OPENING!! SHORT " * (not trade.long) + "-"*20
                                      +'\nSIZE {} \ PRICE {} \ VALUE: {} \n'.format(
                    trade.size,
                    trade.price,
                    trade.value), important=True)
            if(not trade.long):
                self.shortingbudget -= abs(trade.value)

    def notify_order(self, order):
        # information about the order

        dt, dn, ref, data = self.data.datetime.time(), order.data._name, order.ref, order.data

        self.log('{}: Order ref: {} / Type {} / Status {} '.format(
            dt, ref, 'Buy' * order.isbuy() or 'Sell',order.getstatusname()), data=data._name)

        if order.status == order.Submitted:
            return

        if not order.alive():
            price = order.executed.price
            if order.status == order.Completed:
                if (order == self.orefs[data][0]):
                    self.log("{} -- {} ({})--> BUY ESTRATEGICA:  COST {} / PRICE {} / COMMI {}"
                             .format(dt, dn, ref, order.executed.value, order.executed.price, order.executed.comm), data=data._name, important=True)
                    self.orefs[data][0] = None

                elif (order == self.orefs[order.data][1]):
                    self.log("{} -- {} ({}) --> STOP PROFIT ACTIVATED AT PRICE {}".format(
                        dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][1] = None

                elif (order == self.orefs[order.data][2]):
                    self.log("{} -- {} ({})--> STOP LOSS ACTIVATED AT PRICE {}"
                             .format(dt, dn, ref, price), data=data._name, important=True)
                    self.orefs[data][2] = None


                elif (order == self.orefs[order.data][3]):
                    self.log("{} -- {} ({})--> SELL ESTRATEGICA:  COST {} / PRICE {} / COMMI {}"
                             .format(dt, dn, ref, order.executed.value, order.executed.price, order.executed.comm), data=data._name, important=True)
                    self.orefs[data][3] = None

                elif (order == self.orefs[order.data][4]):
                    self.log("{} -- {} ({})--> STOP PROFIT ACTIVATED AT PRICE {}"
                             .format(dt, dn, ref, price),data=data._name, important=True)
                    self.orefs[data][4] = None

                elif (order == self.orefs[order.data][5]):
                    self.log("{} -- {} ({}) --> STOP LOSS ACTIVATED AT PRICE {}"
                             .format(dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][5] = None

                elif (order == self.orefs[order.data][6]):
                    self.log("{} -- {} ({}) LONG POSITION CLOSED {}"
                             .format(dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][6] = None


                elif (order == self.orefs[order.data][7]):
                    self.log("{} -- {} ({}) SHORT POSITION CLOSED {}"
                             .format(dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][7] = None




            elif order.status == order.Canceled:
                if (order == self.orefs[data][0]):
                    self.log("BUY LONG CANCELED!!!!!! {}".format(ref), data=data._name)
                    self.orefs[data][0] = None

                elif (order == self.orefs[order.data][1]):
                    self.log("STOP PROFIT LONG {} CANCELED".format(ref), data=data._name)
                    self.orefs[data][1] = None

                elif (order == self.orefs[order.data][2]):
                    self.log("STOP LOSS LONG {} CANCELED".format(ref), data=data._name)
                    self.orefs[data][2] = None

                elif (order == self.orefs[order.data][3]):
                    self.log("SELL SHORT CANCELLED!!!!!!! {}".format(ref), data=data._name)
                    self.orefs[data][3] = None

                elif (order == self.orefs[order.data][4]):
                    self.log("STOP PROFIT SHORT {} CANCELED".format(ref), data=data._name)
                    self.orefs[data][4] = None

                elif (order == self.orefs[order.data][5]):
                    self.log("STOP LOSS SHORT {} CANCELED".format(ref), data=data._name)
                    self.orefs[data][5] = None

                elif (order == self.orefs[order.data][6]):
                    self.log("{} -- {} ({}) LONG POSITION CLOSED CANCELED{}"
                             .format(dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][6] = None

                elif (order == self.orefs[order.data][7]):
                    self.log("{} -- {} ({}) SHORT POSITION CLOSED CANCELED {}"
                             .format(dt, dn, ref, order.executed.price), data=data._name, important=True)
                    self.orefs[data][7] = None


            elif order.status == order.Rejected:
                self.log("ORDER {} REJECTED".format(ref), data=data._name, important=True)

            elif order.status == order.Margin:
                self.log("ORDER {} MARGIN CALL from {} \ CASH: {}, PRICE {}".format(ref, dn, self.broker.getcash(),
                                                                                  order.data[0]), important=True)

            else:
                print(order.getstatusname() + "-"*20+ "SMT WEIRD"+"-"*20)


    def stop(self):
        print("Ending Portfolio Value:   {}".format(round(self.broker.getvalue(),2)))
        print("Lowest Cash Available:    {}".format(round(self.lowestcash,2)))

        headers = []
        rows = []
        for i in self.params.__dict__.keys():
            headers.append(i)
            rows.append(self.params.__dict__[i])
        print("\nParameters: ")
        if len(headers) >4:
            middle = len(headers)//2
            print(tabulate([headers[:middle], rows[:middle]], headers="firstrow", tablefmt="plain") + "\n")
            print(tabulate([headers[middle:], rows[middle:]], headers="firstrow", tablefmt="plain"))
        else:
            print(tabulate([headers, rows], headers="firstrow", tablefmt="plain"))

    def orderOngoing(self, d):
        if self.orefs[d][0] is not None or self.orefs[d][3] is not None or self.orefs[d][6] is not None or \
                self.orefs[d][7] is not None:
            return True
        else:
            return False

    def newOrders(self, d, openLongCondition, openShortCondition, closeLongCondition, closeShortCondition):
        # Check if an order is pending ... if yes, we cannot send a 2nd one

        if self.orderOngoing(d):
            return

        dt, dn, p = self.data.datetime.time(), d._name, d.close[0]

        p = p * (1.0 + self.p.pentry)

        budget = self.broker.getcash()
        if (self.lowestcash > budget):
            self.lowestcash = budget


        # Check if we are in the market
        if not self.getposition(d) and budget> self.p.minCash:
            # Not yet ... we MIGHT BUY if ...
            if openLongCondition:
                profitPrice = p * (1.0 + self.p.stopprofit)
                valid = datetime.timedelta(self.p.valid)

                sizeLongPosition = round((budget * self.p.percentage) / p)
                if sizeLongPosition > 0:
                    long = self.buy(data=d, size=sizeLongPosition, limit=p, valid=valid, transmit=False)
                    longstopprofit = self.sell(data=d, size=long.size, price=profitPrice, exectype=bt.Order.Limit,
                                         transmit=False, parent=long)
                    longstoploss = self.sell(data=d, size=long.size, trailpercent=self.p.stoploss,
                                        exectype=bt.Order.StopTrail,
                                        transmit=True, parent=long)


                    self.orefs[d] = [long, longstopprofit, longstoploss, None, None, None, None, None]
                    self.log('{} -- {} BUY REQUEST: PRICE {} \ SIZE {}'.format(dt, dn, p, long.size), data=d._name,
                             important=True)

            elif openShortCondition and self.p.shorting and self.shortingbudget>0:
                p = p * (1.0 + self.p.pentry)
                valid = datetime.timedelta(self.p.valid)

                sizeShortPosition = round((self.shortingbudget * self.p.percentage) / p)

                profitPrice = p * (1.0 - self.p.stopprofit)
                if sizeShortPosition > 0:
                    short = self.sell(data=d, size=sizeShortPosition, limit=p, valid=valid, transmit=False)
                    shortstopprofit = self.buy(data=d, size=short.size, price=profitPrice, exectype=bt.Order.Limit,
                                       transmit=False, parent=short)
                    shortstoploss = self.buy(data=d, size=short.size, trailpercent=self.p.stoploss,
                                        exectype=bt.Order.StopTrailLimit,
                                        transmit=True, parent=short)

                    self.orefs[d] = [None, None, None, short, shortstopprofit, shortstoploss, None, None]

                    self.log('{} -- {} SELL REQUEST: PRICE {} \ SIZE {}'
                             .format(dt, dn, p, short.size), data=d._name, important=True)

        else:
            if self.getposition(d).size > 0 and closeLongCondition and self.orefs[d][1] is not None and self.orefs[d][2] is not None:
                self.cancel(self.orefs[d][1])
                self.cancel(self.orefs[d][2])
                close = self.close(d)
                self.orefs[d][6] = close
                self.log('{}: REQUEST TO CLOSE LONG POSITION {} AT PRICE {}'.format(dt, dn, p),
                         data=d._name, important=True)

            elif self.getposition(d).size < 0 \
                    and closeShortCondition and self.orefs[d][4] is not None and self.orefs[d][5] is not None:
                self.cancel(self.orefs[d][4])
                self.cancel(self.orefs[d][5])
                close = self.close(d)
                self.orefs[d][7] = close
                self.log('{}: REQUEST TO CLOSE SHORT POSITION {} AT PRICE {}'
                         .format(dt, dn, p), data=d._name, important=True)


