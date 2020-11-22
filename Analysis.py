import backtrader as bt
from tabulate import tabulate

def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    # Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_short = analyzer.short.total
    total_short_won = analyzer.short.won

    total_long = analyzer.long.total
    total_long_won = analyzer.long.won

    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = round((total_won / total_closed) * 100, 2)

    # Designate the rows
    h1 = ['# Open', '# Closed', '# won' ,'# Lost']
    r1 = [total_open, total_closed, total_won, total_lost]

    h2 = ['# Long', '# long won', 'total short', '# short won']
    r2 = [total_long, total_long_won,total_short, total_short_won]

    h3 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r3 = [strike_rate, win_streak, lose_streak, pnl_net]

    print("Trade Analysis Results:")
    print(tabulate([h1, r1], headers = "firstrow", tablefmt="plain" ))
    print()
    print(tabulate([h2, r2], headers = "firstrow", tablefmt="plain" ))
    print()
    print(tabulate([h3, r3], headers = "firstrow", tablefmt="plain" ))


def printDrawdown(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    # Get the results we are interested in
    maxdrawdown = round(analyzer['max'].drawdown, 2)
    maxmoneydown = round(analyzer['max'].moneydown, 2)
    maxlen = round(analyzer['max'].len, 2)

    # Designate the rows, headers
    h1 = ['Max drawdown', 'Max moneydown', 'Max len']
    r1 = [maxdrawdown, maxmoneydown, maxlen]

    print("Drawdown Analysis:")
    print(tabulate([h1, r1], headers = "firstrow", tablefmt="plain"))

def printTransactions(analyzer):
    # Get the results we are interested in
    averageValue = 0.0
    numberTransactions = 0
    for key in analyzer.keys():
        averageValue += abs(analyzer[key][0][4])
        for item in analyzer[key]:
            averageValue += abs(item[4])
            numberTransactions +=1
    if(numberTransactions != 0):
        averageValue = averageValue/numberTransactions

    print("Average Value Transactions: {}".format(round(averageValue, 2)))
def printAnnualRet(analyzer):
    # Get the results we are interested in
    print("Annualized/Normalized return: {}%".format(round(analyzer['rnorm100'],4)))
    print("Total compound return: {}".format(round(analyzer['rtot'],4)))

def printSharpeRatioandVWR(sharpe, vwr):
    sharpeR = round(sharpe['sharperatio'], 2)

    try:
        vwrR = round(vwr['vwr'], 2)
    except:
        vwrR = None
    print('Sharpe Ratio: {} \nVariability-Weighted Return: {}'.format(sharpeR, vwrR))

def printSQN(analyzer):
    sqn = round(analyzer.sqn, 2)
    if analyzer.trades < 30:
        print("SQN: {} (not very reliable, # trades < 30)".format(sqn))
    else:
        print('SQN: {}'.format(sqn))

def startAnalyzing(cerebro):
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpeRatio", riskfreerate=0.00, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
    cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="annualret")

    print()

def printAnalysis(results):
    print()

    print(" "*39 + "  ANALYSIS  " + " "*39)

    if hasattr(results, 'analyzers'):
        ta = results.analyzers.ta.get_analysis()
        sharpeRatio = results.analyzers.sharpeRatio.get_analysis()
        sqn = results.analyzers.sqn.get_analysis()
        drawdown = results.analyzers.drawdown.get_analysis()
        transactions = results.analyzers.transactions.get_analysis()
        vwr = results.analyzers.vwr.get_analysis()
        annualret = results.analyzers.annualret.get_analysis()

        printAnnualRet(annualret)
        print()
        printTransactions(transactions)
        print()
        printTradeAnalysis(ta)
        print()
        printDrawdown(drawdown)
        print()
        printSharpeRatioandVWR(sharpeRatio, vwr)
        printSQN(sqn)
        print("\n" +"*"*86)


