# TODO

## goal

- always day one
- keep simple
- optimize when needed
- inspiring, fantastically beautiful graphs

## tasks

- store req dis in Data
  - rename to di: dict
  - store/use req_di from init
  - store rec_di sorted by key
  - check for no None key/col
- rewrite big_table() to not use excessive areays
  - create empty df, write to it directly

- run w/o optimization, check time
- compare time running w/o asserts

- optimize execute if possible
  - try pre-compiling
    - where?
  - try addressing as normal array/int/hash
  - load all ops, execute together as a program for every slice
    - mark dis that are should not be optimized
    - do not store in table dis that are marked for optimizarion
      - create locally in the context of one op execution row
      - how many per row?
    - in debug mode do not optimize
  - google lightweight program from list of ops on table
- check if op optimization does not leave anything behind

- remove unneeded data copy
- review all places where data is transfered between sets, lists, arrays

- add plot as 3d surface
- find optimal sma cross parameters for daily SPX

- publish tool
- publish sma cross experiment

- add simple broker simulation
- add summary statistics
- compare to known framework

- test RSI strategy
- test parameter optimization
- run parameter optimization

- run profiling
- find bottlenecks
  - strip unused columns from pd
  - run in chunks, find optimal chunk size
  - cache/store intermediate results
- try compiling
- try separating calls: vectors / sequences
  - run vectors first over all data at once
  - run sequrnces after
- try optimizing

- find decision making points, where market slows down to make a decision
  and either goes up or down
  - best place to enter/exit
- try different options for best entry/exist points
- try different strategies relative to such points

- calculate probabilities at different point in time for different moves
- try graphing a heatmap of probabilities (experiment with resolution) -
  where the price would end based on combination of triggered strategies
- multiplication of such heatmaps based on triggers

- find some weak/simple working strategy (ma, rsi)

- try market heatmap strategy

- add tests?

- describe in article
- create ibkr or binance account
- setup bot

strategies:

- how to find the best strategy?
  - take some rule to buy/sell, parametrize, find best parameters
  - create a probabalistic heatmap of the market future, based on indicators
    - list indicators
    - for every indicator find probability distribution over time for
      predicting a market move from current point to some quadrant
      - e.g. after sma20>sma5
        - price goest up
          - probability of it over time to stop at a particular distance range
            from the starting point
          - higher probability - brighter heatmap
    - overlap indicators

suggestions:

- performance test - graph table size/execution time
