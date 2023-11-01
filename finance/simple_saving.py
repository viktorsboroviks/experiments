import vfin
import vfin_ops

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX'),
})

# TODO: change period to 1 month
time_seq = vfin_ops.TimePeriodSeq('year')

vfin.BacktestEngine(
    data,
    time_seq.operations()
).run()

# debug
time_seq.debug_plot(data.big_table(), 'test.svg')

# TODO: Add saving strategy, debug, result
