'''
Experiment for testing SMA cross strategy.
'''
import datetime
from symbol import parameters
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
                                 di={'close': vfin.DataInfo('^SPX', 'Close')},
                                 slippage=0.5)
monthly_alarm = vtime.Alarm('monthly')

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
    ops += opg.ops()

vfin.BacktestEngine(data, ops).run()

res_info = []
for opg in sma_cross_opgens:
    res_info += [
        vstats.StrategyInfo(opg.name, opg, data.big_table()),
    ]

vstats.print_results(res_info)
vstats.plot_results(res_info, 'test_sma_cross_comparison.html')


# generate params
# params = [param for param in vparams.cortesian_product({'smth': values,
#                                                         'smth': values,
#                                                         'smth': values})
#
## generate opgens
# opgs = [strategy.sma_cross.SmaCrossOpGen(param,
#                                          param,
#                                          param) for param in params]
#
## generate operations
# ops = [opg.ops() for opg in opgs]
#
## backtest
# bt = vfin.BacktestEngine(data,
#                          ops
# ).run()
#
# save for reuse
# pickle_data = [opgs, bt]
# with open(filename, "wb") as f:
#     pickle.dump(pickle_data, f)
# with open(filename, "rb") as f:
#     pickle_data = pickle.load(f)
# 
## generate sis
# sis = [vstats.StrategyInfo(opg.name,
#                            opg,
#                            bt) for opg in opgs]
#
## generate results
# vstats.print_results(sis)
# vstats.plot_results(sis, 'test_sma_cross_comparison.html')
# vstats.plot_surface()