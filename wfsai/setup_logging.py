"""
Used for consistent logger behaviour across all modules.  

Usage:
`from wfsai.setup_logging import logger`
    
---  
    
"""

# setup_logging.py
# Import in all required scripts to get consistent logger behaviour

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wfsai')