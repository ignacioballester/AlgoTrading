import backtrader as bt
import datetime
import Strategies.StrategyTemplate as st
from collections import defaultdict


# Create a Stratey
class RSI_strategy(st.StrategyTemplate):
    params = (('buySignal', 30),
              ('sellSignal', 70),
              ('closeShortSignal', 50),
              ('closeLongSignal', 50),
              ('shorting', True),
              ('shortingbudget', 10000),
              ('minCash', 8000),
              ('percentage', 0.1),
              ('pentry', 0.015),
              ('stopprofit', 0.03),
              ('stoploss', 0.0015),
              ('valid', 10),
              ('printAllLogs', False),
              ('printImportantLogs', False),
              )

    def __init__(self):
        # To keep track of pending orders
        self.orefs = dict()

        # Add 3 MovingAverageSimple indicator per stock
        self.rsi = dict()
        self.lowestcash = self.broker.getcash()
        self.shortingbudget = self.p.shortingbudget
        for data in self.datas:
            self.rsi[data] = bt.indicators.RSI(data)
            self.orefs[data] = [None, None, None,None,None,None,None,None]

    def next(self):
        # Simply log the closing price of the series from the reference
        for i, d in enumerate(self.datas):
            # Check if an order is pending ... if yes, we cannot send a 2nd one


            rsi = self.rsi[d]
            openLongCondition = rsi[0] < self.p.buySignal and d.close[0]/d.close[-1]>1.02
            closeLongCondition = rsi[0] > self.p.closeLongSignal

            openShortCondition = rsi[0] > self.p.sellSignal and d.close[-1]/d.close[0]>1.02
            closeShortCondition = rsi[0] > self.p.closeShortSignal

            self.newOrders(d, openLongCondition, openShortCondition, closeLongCondition, closeShortCondition)
