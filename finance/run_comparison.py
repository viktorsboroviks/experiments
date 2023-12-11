'''
Experiment for testing money saving.
'''
import datetime
import vfin
import vstats
import vtime
import strategies.saving
import strategies.money_avg
import strategies.sma_cross

instrument = vfin.InstrumentInfo(ticker_name='^SPX',
                                 close_di=vfin.DataInfo('^SPX', 'Close'),
                                 slippage=0.5)

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2000, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})
monthly_alarm = vtime.Alarm('monthly')

saving_opgen = strategies.saving.SavingOpGen(
    initial_cash=1000,
    add_cash=100,
    add_cash_alarm=monthly_alarm)

money_avg_opgen = strategies.money_avg.MoneyAvgOpGen(
    price_info=instrument,
    initial_cash=1000,
    add_cash=100,
    add_cash_alarm=monthly_alarm)

sma_cross_opgen = strategies.sma_cross.SmaCrossOpGen(
    price_info=instrument,
    initial_cash=1000,
    add_cash=100,
    add_cash_alarm=monthly_alarm,
    coefs={'long entry slow sma': 200,
           'long entry fast sma': 50,
           'long exit slow sma': 200,
           'long exit fast sma': 50}
)
#           'short entry slow sma': 200,
#           'short entry fast sma': 50,
#           'short exit slow sma': 200,
#           'short exit fast sma': 50,
#    })
# TODO: investigate and fix

vfin.BacktestEngine(
    data,
    saving_opgen.ops() +
    money_avg_opgen.ops() +
    sma_cross_opgen.ops()
).run()

vstats.print_results([
    vstats.StrategyInfo('saving', saving_opgen, data.big_table()),
    vstats.StrategyInfo('money_avg', money_avg_opgen, data.big_table()),
    vstats.StrategyInfo('sma_cross', sma_cross_opgen, data.big_table()),
    ])

vstats.plot_results([
    vstats.StrategyInfo('saving', saving_opgen, data.big_table()),
    vstats.StrategyInfo('money_avg', money_avg_opgen, data.big_table()),
    vstats.StrategyInfo('sma_cross', sma_cross_opgen, data.big_table()),
    ], 'test_results.html')

# debug
saving_opgen.debug_plot(data.big_table(), 'test_saving.html')
money_avg_opgen.debug_plot(data.big_table(), 'test_money_avg.html')
sma_cross_opgen.debug_plot(data.big_table(), 'test_sma_cross.html')
