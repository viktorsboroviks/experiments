'''
Experiment for testing SMA cross strategy.
'''
import datetime
import vfin
import vlog
import vparams
import vstats
import vtable
import vtime
import strategies.sma_cross


vlog.configure('debug')

# fetch input dataframes
dfs = {
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2000, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
}

# generate parameters
params = list(vparams.cortesian_product({
            'long entry slow sma': list(range(5, 7)),
            'long entry fast sma': list(range(5, 7)),
            'short entry slow sma': list(range(5, 7)),
            'short entry fast sma': list(range(5, 7))
        }))

# generate operation generators
instrument = vfin.InstrumentInfo(ticker_name='^SPX',
                                 di={'close': vtable.DataInfo('^SPX', 'Close')},
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
be = vfin.BacktestEngine(ops=ops, dfs=dfs)
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
# TODO: remove debug print
print(f'total strategies analized: {len(sis)}')
# TODO: vstats.plot_surface()
