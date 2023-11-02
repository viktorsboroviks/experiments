import datetime
import vfin
import vfin_ops
import strategies.saving

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

time_seq = vfin_ops.TimePeriodSeq('Monthly timer', 'month')

cash_saving1_seq = strategies.saving.CashSaving(
    strategy_name='Saving w/o adding',
    initial_cash=1000,
    currency_name='EUR')

cash_saving2_seq = strategies.saving.CashSaving(
    strategy_name='Saving while adding',
    initial_cash=1000,
    add_cash=100,
    add_cash_when='month',
    currency_name='EUR')

vfin.BacktestEngine(
    data,
    time_seq.get_ops() + 
    cash_saving1_seq.get_ops() +
    cash_saving2_seq.get_ops()
).run()

# debug
time_seq.debug_plot(data.big_table(), 'test_time.svg')
cash_saving1_seq.debug_plot(data.big_table(), 'test_saving1.svg')
cash_saving2_seq.debug_plot(data.big_table(), 'test_saving2.svg')


# TODO: Add saving strategy, debug, result
# TODO: Decide what to do with timeperiod/alarm and a strategy
# TODO: Review code - clean up, simplify!
