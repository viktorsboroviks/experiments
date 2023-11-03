'''
Experiment for testing money saving.
'''
import datetime
import vfin
import vfin_ops
import strategies.saving

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

saving1_opgen = strategies.saving.SavingOpGen(
    name='Saving w/o adding',
    initial_value=1000)

saving2_opgen = strategies.saving.SavingOpGen(
    name='Saving while adding',
    initial_value=1000,
    add_value=100,
    add_alarm='monthly')

vfin.BacktestEngine(
    data,
    saving1_opgen.ops() +
    saving2_opgen.ops()
).run()

# debug
saving1_opgen.debug_plot(data.big_table(), 'test_saving1.svg')
saving2_opgen.debug_plot(data.big_table(), 'test_saving2.svg')

# TODO: Add money averaging
# TODO: Add accumulating final function to show total
