# -*- coding: utf-8 -*-
from .transformations import (
    ensure_ids_are_unique,
    ensure_mandatory_properties,
    fix_ecoinvent_parameters,
    manage_activity_links,
    pv_cleanup,
    validate_markets,
    variable_names_are_unique,
)
from .transformations.cutoff import (
    cleanup_activity_links,
    cutoff_allocation,
    handle_waste_outputs,
)
from .transformations.cutoff.cleanup import (
    drop_rp_activity_links,
    drop_zero_amount_activity_links,
    remove_consequential_exchanges,
)
from .transformations.locations import link_markets_by_pv
from .transformations.consequential import (
    ensure_byproducts_have_alternative_production,
    handle_constrained_markets,
    link_markets_by_technology_level,
    split_combined_production,
)


class Configuration(object):
    """This is a dummy class, to be filled in with code that can parse various ways for defining a system model in a list of Python functions, including currying, etc."""
    def __init__(self):
        self.functions = []

    def __iter__(self):
        return iter(self.functions)


# Default config for now is cutoff
cutoff_config = [
    ensure_ids_are_unique,
    variable_names_are_unique,
    # There are a *lot* of missing mandatory properties
    # No point adding them to this report
    # ensure_mandatory_properties,
    validate_markets,
    fix_ecoinvent_parameters,
    pv_cleanup,
    remove_consequential_exchanges,
    cleanup_activity_links,
    manage_activity_links,
    handle_waste_outputs,
    cutoff_allocation,
    drop_rp_activity_links,
    link_markets_by_pv,
    # extrapolate to database reference year
    # normalize_reference_production_amount
    # final output processing
]

consequential_config = [
    ensure_ids_are_unique,
    variable_names_are_unique,
    validate_markets,
    fix_ecoinvent_parameters,
    pv_cleanup,
    drop_zero_amount_activity_links,
    split_combined_production,
    handle_constrained_markets,
    manage_activity_links,
    ensure_byproducts_have_alternative_production,
    link_markets_by_technology_level,
    # extrapolate to database reference year
    # normalize_reference_production_amount
    # final output processing
]
