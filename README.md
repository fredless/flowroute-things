# flowroute-things

My collection of tiny utils to help admin a flowroute account. Makes use of [flowroute's public API](https://developer.flowroute.com/api/).

## [did_block_finder.py](did_block_finder.py)
Search out contiguous blocks of DIDs available for purchase

With the following specification:
``` python
STARTS_WITH = 1408740
MIN_SIZE = 15
```

..some typical output:
```
Block of 22: 14087407578 - 14087407599
Block of 52: 14087407601 - 14087407652
Block of 31: 14087407667 - 14087407697
```

Can also search for interesting digit sequences, see code.

## [did_block_purchaser.py](did_block_purchaser.py)
Buy continguous blocks of DIDs available for purchase

With the following specification:
``` python
STARTS_WITH = 14085551200
ENDS_WITH = 14085551214
```

...some typical output:
```
Purchasing number: 14085551200... purchased
Purchasing number: 14085551201... purchased
...
Purchasing number: 14085551214... purchased
```