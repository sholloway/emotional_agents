
"""
Important!!!: 
Reloading modules only works if they're in the same folder as the __init__.py file.
"""
import importlib
import sys 

import emotional_agents.scene

def reload():
  """Don't change unless you know what you're doing.
  This is responsible for reloading the project. It will automatically reload
  any module in the emotional_agents package that is imported above.
  """
  [ 
    importlib.reload(sys.modules[module_name]) 
    for module_name in list( 
      filter(
        lambda i: i.startswith('emotional_agents.'), 
        sys.modules.keys()
      )
    ) 
  ]