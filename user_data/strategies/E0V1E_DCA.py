import math
import logging
from datetime import datetime, timedelta, timezone
from freqtrade.persistence import Trade
import time
from typing import Dict, List, Optional
from E0V1E import E0V1E

logger = logging.getLogger(__name__)

class E0V1E_DCA (E0V1E):

    position_adjustment_enable = True
    initial_safety_order_trigger = -0.02
    max_entry_position_adjustment = 3
    safety_order_step_scale = 2
    safety_order_volume_scale = 1.8
    
    max_so_multiplier = (1 + max_entry_position_adjustment)
    if(max_entry_position_adjustment > 0):
        if(safety_order_volume_scale > 1):
            max_so_multiplier = (2 + (safety_order_volume_scale * (math.pow(safety_order_volume_scale,(max_entry_position_adjustment - 1)) - 1) / (safety_order_volume_scale - 1)))
        elif(safety_order_volume_scale < 1):
            max_so_multiplier = (2 + (safety_order_volume_scale * (1 - math.pow(safety_order_volume_scale,(max_entry_position_adjustment - 1))) / (1 - safety_order_volume_scale)))

    # Since stoploss can only go up and can't go down, if you set your stoploss here, your lowest stoploss will always be tied to the first buy rate
    # So disable the hard stoploss here, and use custom_sell or custom_stoploss to handle the stoploss trigger
    stoploss = -1

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float,
                    current_profit: float, **kwargs):

        tag = super().custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs)
        if tag:
            return tag
            
        enter_tag = 'empty'
        if hasattr(trade, 'enter_tag') and trade.enter_tag is not None:
            enter_tag = trade.enter_tag
        enter_tags = enter_tag.split()

        if current_profit <= -0.1:
            return f'stop_loss ({enter_tag})'

        return None

    # Let unlimited stakes leave funds open for DCA orders
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            entry_tag: Optional[str], side: str, **kwargs) -> float:
                            
        return proposed_stake / self.max_so_multiplier

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float, min_stake: float,
                              max_stake: float, **kwargs) -> Optional[float]:
        if current_profit > self.initial_safety_order_trigger or current_profit > -0.09:
            return None

        filled_entries = trade.select_filled_orders(trade.entry_side)
        count_of_entries = len(filled_entries)
        if count_of_entries < self.max_entry_position_adjustment:
            return filled_entries[0].cost
        return None
