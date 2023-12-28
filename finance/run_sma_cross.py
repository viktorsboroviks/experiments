'''
Experiment for testing SMA cross strategy.
'''
import datetime
import vfin
import vstats
import vtime
import vparams
import strategies.sma_cross


# fetch data
data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2000, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

# generate parameters
params = [param for param in vparams.cortesian_product({
            'long entry slow sma': [a for a in range(5, 8)],
            'long entry fast sma': [a for a in range(5, 8)],
            'short entry slow sma': [a for a in range(5, 8)],
            'short entry fast sma': [a for a in range(5, 8)]
        })]

# generate operation generators
instrument = vfin.InstrumentInfo(ticker_name='^SPX',
                                 di={'close': vfin.DataInfo('^SPX', 'Close')},
                                 slippage=0.5)
monthly_alarm = vtime.Alarm('monthly')
opgs = [strategies.sma_cross.SmaCrossOpGen(
            price_info=instrument,
            initial_cash=1000,
            add_cash=100,
            add_cash_alarm=monthly_alarm,
            params=param,
            name=f'sma({param.values()})') for param in params]

# generate operations
ops = []
for opg in opgs:
    ops += opg.ops()

# backtest
be = vfin.BacktestEngine(data, ops)
bt = be.run()

# TODO: save for reuse
# pickle_data = [opgs, bt]
# with open(filename, "wb") as f:
#     pickle.dump(pickle_data, f)
# with open(filename, "rb") as f:
#     pickle_data = pickle.load(f)

# generate strategy infos
sis = [vstats.StrategyInfo(opg.name,
                           opg,
                           bt) for opg in opgs]

# generate results
vstats.print_results(sis)
vstats.plot_results(sis, 'test_sma_cross_comparison.html')
# TODO: vstats.plot_surface()

