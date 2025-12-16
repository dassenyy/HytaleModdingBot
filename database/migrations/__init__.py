import os
import importlib
from typing import List
from ..migration import Migration

def discover_migrations() -> List[Migration]:
    """Dynamically discover and instantiate all migration classes"""
    migrations = []
    migrations_dir = os.path.dirname(__file__)
    
    # Get all Python files in the migrations directory
    for filename in os.listdir(migrations_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'.{module_name}', package=__name__)
                
                # Find Migration classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Migration) and 
                        attr != Migration):
                        # Instantiate the migration
                        migration_instance = attr()
                        migrations.append(migration_instance)
                        
            except Exception as e:
                print(f"Warning: Could not load migration from {filename}: {e}")
    
    return migrations