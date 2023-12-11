'''
Experiment for testing SMA cross strategy.
'''
import datetime
import vfin
import vstats
import vtime
import strategies.sma_cross

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2000, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

instrument = vfin.InstrumentInfo(ticker_name='^SPX',
                                 close_di=vfin.DataInfo('^SPX', 'Close'),
                                 slippage=0.5)
monthly_alarm = vtime.Alarm('monthly')

# TODO: write a proper
coefs = (
    (200, 50, 200, 50),
    (150, 50, 150, 50),
    (100, 50, 100, 50),
    (50, 25, 50, 25),
    (20, 5, 20, 5),
)

sma_cross_opgens = []
for coef in coefs:
    sma_cross_opgens += [
        strategies.sma_cross.SmaCrossOpGen(
            price_info=instrument,
            initial_cash=1000,
            add_cash=100,
            add_cash_alarm=monthly_alarm,
            coefs={'long entry slow sma': coef[0],
                   'long entry fast sma': coef[1],
                   'long exit slow sma': coef[2],
                   'long exit fast sma': coef[3]}
        )
    ]

ops = []
for opg in sma_cross_opgens:
    ops += [opg.ops()]

vfin.BacktestEngine(data, ops).run()

res_info = []
for opg in sma_cross_opgens:
    res_info += [
        vstats.StrategyInfo(str(coefs[opg.index]), opg, data.big_table()),
    ]

vstats.print_results(res_info)
vstats.plot_results(res_info, 'test_sma_cross_comparison.html')
