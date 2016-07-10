# -*- coding: utf-8 -*-
import pandas as pd
from copy import copy
import os
import numpy as np
from .. import utils
import time

def dummy():
    return ''
    
def available_production_volume(datasets, logger, support_excel_folder, support_pkl_folder):
    """Calculates available production volume for market shares by removing 
        consumption by activity links"""
    
    #first, an activity link overview is required
    activity_overview = utils.open_file(support_pkl_folder, 'activity_overview')
    activity_link_overview = build_activity_link_overview(activity_overview, datasets)
    
    #write the activity link overview for reference
    filename = 'activity_link_overview.xlsx'
    writer = pd.ExcelWriter(os.path.join(support_pkl_folder, filename))
    columns = ['activity name', 'location', 'reference product', 
               'exchange name', 'activity link activity name', 
               'activity link location', 'amount', 'consumed amount', 
               'note']
    activity_link_overview.to_excel(writer, 'activity_link_overview', 
        index = False, merge_cells = False, columns = columns)
    
    #removing loss and conditional exchanges for further calculation, as they have
    #no effect on PV change
    activity_link_overview = activity_link_overview[activity_link_overview['note'] == '']
    activity_link_overview = pd.pivot_table(activity_link_overview, 
        index = ['activity link activity name', 'activity link location', 'exchange name'], 
        values = ['consumed amount'], aggfunc = np.sum)
    
    #Building a data frame compiling PV, PV consumed and PV available
    available_PV_overview = build_available_PV_overview(datasets, 
        activity_overview, activity_link_overview)
    
    #write it to excel for reference
    columns = ['activity name', 'location', 'exchange name', 'production volume', 
               'consumed by activity links', 'available production volume']
    available_PV_overview.to_excel(writer, 'available_PV_overview', columns = columns, 
        index = False, merge_cells = False)
    utils.save_file(available_PV_overview, support_pkl_folder, 'available_PV_overview')
    writer.save()
    writer.close()
    
    #write in the exchanges the available PV
    datasets = write_availabe_PV_in_exchanges(datasets, available_PV_overview)
    
    return datasets

def build_activity_link_overview(activity_overview, datasets):
    activity_overview = activity_overview.set_index(['activity id', 'exchange name']
            ).sortlevel(level=0)
    activity_link_overview = {}
    for dataset in datasets:
        assert 'allocate_cutoff' in dataset['history'].keys()
        ref_exc = utils.get_reference_product(dataset)
        for exc in dataset['exchanges']:
            if 'activity link' in exc and exc['type'] != 'reference product': # why link in RP?
                #qualitative information about the exchange
                sel = activity_overview.loc[(exc['activity link'], exc['name'])]
                if type(sel) == pd.core.frame.DataFrame:
                    sel = sel.iloc[0]
                to_add = {'activity name': dataset['name'], 
                          'location': dataset['location'], 
                    'reference product': dataset['main reference product'], 
                    'exchange name': exc['name'], 
                    'amount': exc['amount'], 
                    'activity link activity name': sel['activity name'], 
                    'activity link location': sel['location']
                    }
                
                #how much is consumed?
                to_add['consumed amount'] = abs(to_add['amount'] / ref_exc['amount'
                    ] * ref_exc['production volume']['amount'])
                
                #might be a loss or a conditional exchange
                if exc['activity link'] == dataset['id']:
                    to_add['note'] = 'loss'
                elif to_add['amount'] < 0. and dataset['type'] == 'market activity':
                    to_add['note'] = 'conditional exchange'
                else:
                    to_add['note'] = ''
                activity_link_overview[len(activity_link_overview)] = copy(to_add)
    activity_link_overview = pd.DataFrame(activity_link_overview).transpose()
    
    return activity_link_overview
    

def build_available_PV_overview(datasets, activity_overview, activity_link_overview):
    available_PV_overview = {}
    activity_overview = activity_overview.set_index(['activity name', 'location', 'exchange name'])
    
    for dataset in datasets:
        #fetch information already in the exchange
        exc = utils.get_reference_product(dataset)
        to_add = {'activity name': dataset['name'], 
                  'location': dataset['location'], 
                    'exchange name': exc['name'], 
                    'production volume': exc['production volume']['amount']}
        
        #get the information in the activity link overview
        index = (dataset['name'], dataset['location'], dataset['main reference product'])
        if index in set(activity_link_overview.index):
            sel = activity_link_overview.loc[index]
            to_add['consumed by activity links'] = sel['consumed amount']
            if sel['consumed amount'] < exc['available production volume']:
                available = exc['available production volume'] - sel['consumed amount']
            else:
                available = 0.
        else:
            to_add['consumed by activity links'] = 0.
            available = exc['available production volume']
        to_add['available production volume'] = copy(available)
        available_PV_overview[len(available_PV_overview)] = copy(to_add)
    
    available_PV_overview = pd.DataFrame(available_PV_overview).transpose()
    
    return available_PV_overview


def write_availabe_PV_in_exchanges(datasets, available_PV_overview):
    available_PV_overview = available_PV_overview.set_index(['activity name', 
        'location', 'exchange name']).sortlevel(level=0)
    
    for dataset in datasets:
        for exc in dataset['exchanges']:
            if exc['type'] in ['reference product', 'byproduct'
                    ] and exc['name'] == dataset['reference product']:
                exc['available production volume'] = available_PV_overview.loc[
                    (dataset['name'], dataset['location'], exc['name']), 
                    'available production volume']
        dataset['history']['calculate_available_PV'] = time.ctime()
    return datasets