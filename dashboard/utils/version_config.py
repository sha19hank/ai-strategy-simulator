"""
Version configuration for dashboard compatibility
Maps column names and features between Version 1 and Version 2
"""

VERSION_CONFIGS = {
    'version1': {
        'display_name': 'Version 1: Foundation',
        'data_path': 'version1/experiments/logs/evaluation',
        'required_columns': [
            'episode', 'step', 'agent', 'price', 'rd_investment',
            'innovation_stock', 'market_share', 'marginal_cost',
            'quantity', 'profit_step', 'cum_profit', 'effective_demand',
            'economic_regime', 'substitute_pressure'
        ],
        'optional_columns': [],
        'charts': {
            'prices': True,
            'profits': True,
            'market_share': True,
            'innovation': True,
            'hhi': True,
            'regime_overlay': True,
        },
        'features': {
            'bankruptcy': False,
            'market_entry': False,
            'human_play': False,
        }
    },
    'version2': {
        'display_name': 'Version 2: Extensions',
        'data_path': 'version2/experiments/logs/evaluation',
        'required_columns': [
            'episode', 'step', 'agent', 'price', 'rd_investment',
            'innovation_stock', 'market_share', 'marginal_cost',
            'quantity', 'profit_step', 'cum_profit', 'effective_demand',
            'economic_regime', 'substitute_pressure'
        ],
        'optional_columns': [
            'is_bankrupt', 'entry_turn', 'human_decision'
        ],
        'charts': {
            'prices': True,
            'profits': True,
            'market_share': True,
            'innovation': True,
            'hhi': True,
            'regime_overlay': True,
            'bankruptcy_events': True,
            'entry_exit': True,
        },
        'features': {
            'bankruptcy': True,
            'market_entry': True,
            'human_play': True,
        }
    }
}

def get_version_config(version_key):
    """Get configuration for specified version"""
    return VERSION_CONFIGS.get(version_key, VERSION_CONFIGS['version1'])

def detect_version_from_columns(columns):
    """Auto-detect version based on available columns"""
    columns_set = set(columns)
    
    # Check for Version 2 specific columns
    v2_columns = {'is_bankrupt', 'entry_turn', 'human_decision'}
    if v2_columns.intersection(columns_set):
        return 'version2'
    
    return 'version1'
