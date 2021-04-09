import pandas as pd
from typing import Union
import time
import unittest
import random
from deribitsimplebot.interface import IBotStore

class CSVBotStroe(IBotStore):

    def __init__(self, file: str, data: pd.DataFrame = None,
                save_param:dict = None,**pandas_param_read):
        super().__init__()

        self.file = file
        self.save_param = save_param

        self.df = (data
                    if not data is None
                    else pd.read_csv(file, delimiter=';', **pandas_param_read)
                )

        self.df = (
            self.df.set_index(
                self.df['id']
            )
        )

        self.df = self.df.astype({
                'active':'int64',
                'price':'float64',
                'amount':'float64',
                'real_create':'datetime64',
                'real_update':'datetime64',
                'create':'datetime64',
                'update':'datetime64'
            })

    def get(self, order_id: Union[int, str, None] = None, param: dict = {}, 
            order_by: dict[str, str] = {}) -> Union[None, dict, list[dict]]:

        query = ''
        _real_param = {}

        if not order_id is None:
            return (self.df.loc[order_id].to_dict() if order_id in self.df.index else None)
        elif len(param.keys()):

            _p = []
            
            for i in param:

                _cd = {
                    'operation' : '==',
                    'value' : param[i]
                }
 
                if isinstance(param[i], list):
                    _cd['operation'] = 'in'
                elif isinstance(param[i], dict):
                    _cd = param[i]

                if 'raw' in _cd:
                    _p.append(_cd['raw'])
                else:
                    _real_param[i] = _cd['value']

                    _p.append(f'(`{i}` {_cd["operation"]} @_real_param["{i}"])')

            query=' and '.join(_p)

        if len(order_by):
            _ob = order_by.popitem()
            _df = self.df.sort_values(by = _ob[0], ascending = (_ob[1]=='asc'))
        else:
            _df = self.df

        _res = _df.query(query)

        order = []
        for i, row in _res.iterrows():
            order.append(row.to_dict())

        return order


    def insert(self, order: dict, other_param: dict = {},
                return_is_active: bool = True, modify_active: bool = True):
        return self.__write(
                is_insert = True, 
                order = order, 
                other_param = other_param,
                return_is_active = return_is_active,
                modify_active = modify_active,
                field_map = {
                    'id' : 'order_id',
                    'group_id' : 'label',
                    'instrument' : 'instrument_name',
                    'state' : 'order_state',
                    'type' : 'order_type',
                    'direction': 'direction',
                    'price' : 'price',
                    'amount' : 'amount',
                    'real_create' : 'creation_timestamp',
                }
            )


    def update(self, order_id: Union[int, str, None], order: dict, other_param: dict = {},
                return_is_active: bool = True, modify_active: bool = True):
        return self.__write(
                is_insert = False, 
                order_id = order_id,
                order = order, 
                other_param = other_param,
                return_is_active = return_is_active,
                modify_active = modify_active,
                field_map = {
                    'state' : 'order_state',
                    'type' : 'order_type',
                    'price' : 'price',
                    'amount' : 'amount',
                    'update' : 'update',
                    'real_update' : 'last_update_timestamp',
                }
            )

    def __write(self, is_insert: bool, field_map: dict, order: dict = None,
                order_id: Union[int, str, None] = None, other_param:dict = {},
                return_is_active: bool = True, modify_active: bool = True):

        _order = { **other_param }

        if is_insert:
            record = dict.fromkeys(self.df.columns)
            _order['create'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
            _order['active'] = 1
        elif not order_id is None:
            record = self.get(order_id)
            _order['update'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        else:
            record = None

        if record is None:
            return None

        for i in field_map :

            if (i == 'real_create' or i == 'real_update') and (field_map[i] in order):
                _order[i] = pd.to_datetime(
                    time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(int(order[field_map[i]]/1000))
                    )
                )
            elif (i == 'update'):
                _order[i] = pd.to_datetime(
                    time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
                )
            elif (field_map[i] in order):
                _order[i] = order[field_map[i]]

        if is_insert==False and 'active' in _order:
            modify_active = False

        if modify_active and (_order['state'] != 'open') and (_order['state'] != 'filled'):
            _order['active'] = 0
            _order['active_comment'] = 'Order is not open or filled'

        for i in record:
            if i in _order:
                record[i] = _order[i]

        if is_insert:
            self.df = self.df.append(record,ignore_index=True)
        else:
            self.df.loc[record['id']] = record.values()

        self.df.to_csv(self.file,index = False, sep=';', **self.save_param)
        self.df = self.df.set_index(self.df['id'])
        
        if return_is_active:
            return record if record['active']>0 else None
        else:
            return record
