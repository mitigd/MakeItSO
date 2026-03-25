import pycdlib
from datetime import datetime

# Global state for the ISO
_state = {
    'iso': None,
    'path': None,
    'current_dir': '/',
    'is_loaded': False
}

def new_iso():
    """Initialize a new ISO."""
    if _state['iso']:
        _state['iso'].close()
    
    _state['iso'] = pycdlib.PyCdlib()
    _state['iso'].new(joliet=3)
    _state['is_loaded'] = True
    _state['path'] = None
    _state['current_dir'] = '/'

def open_iso(path):
    """Open an existing ISO file."""
    if _state['iso']:
        _state['iso'].close()
    
    _state['iso'] = pycdlib.PyCdlib()
    try:
        _state['iso'].open(path)
        _state['is_loaded'] = True
        _state['path'] = path
        _state['current_dir'] = '/'
        return True
    except Exception as e:
        print(f"Error opening ISO: {e}")
        return False

def save_iso(path):
    """Save the ISO to a file."""
    if not _state['is_loaded']:
        return False
    try:
        _state['iso'].write(path)
        _state['path'] = path
        return True
    except Exception as e:
        print(f"Error saving ISO: {e}")
        return False

def list_dir(path=None):
    """List items in the current or specified ISO directory."""
    if not _state['is_loaded']:
        return []
    
    target_path = path if path else _state['current_dir']
    if not target_path.endswith('/'):
        target_path += '/'
        
    items = []
    iso_obj = _state['iso']
    
    try:
        # Detect available namespace
        kwargs = {}
        if iso_obj.has_joliet():
            kwargs['joliet_path'] = target_path
        elif iso_obj.has_rock_ridge():
            kwargs['rock_ridge_path'] = target_path
        else:
            kwargs['iso_path'] = target_path
            
        for entry in iso_obj.list_children(**kwargs):
            if entry.is_dot() or entry.is_dotdot():
                continue
            
            # Try to get the name from the best namespace
            name = None
            if iso_obj.has_joliet():
                try: name = entry.file_identifier().decode('utf-16be').replace('\x00', '')
                except: pass
            
            if not name:
                name = entry.file_identifier().decode('utf-8', errors='replace')
                
            if ';' in name:
                name = name.split(';')[0]
            
            items.append({
                'name': name,
                'is_dir': entry.is_dir(),
                'size': entry.data_length,
                'modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        print(f"Error listing {target_path} with {kwargs}: {e}")
        
    return items

def add_file(local_path, iso_path):
    if not _state['is_loaded']: return False
    iso_obj = _state['iso']
    try:
        kwargs = {}
        # We always want to add to all available namespaces
        if iso_obj.has_joliet():
            kwargs['joliet_path'] = iso_path
        if iso_obj.has_rock_ridge():
            kwargs['rock_ridge_path'] = iso_path
        
        # ISO9660 is always present, but we need to ensure the name is compliant
        # if not using RR or Joliet. For now, we assume simple mapping.
        kwargs['iso_path'] = iso_path
        
        iso_obj.add_file(local_path, **kwargs)
        return True
    except Exception as e:
        print(f"Error adding file {iso_path}: {e}")
        return False

def add_dir(iso_path):
    if not _state['is_loaded']: return False
    iso_obj = _state['iso']
    try:
        kwargs = {}
        if iso_obj.has_joliet(): kwargs['joliet_path'] = iso_path
        if iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = iso_path
        kwargs['iso_path'] = iso_path
        
        iso_obj.add_directory(**kwargs)
        return True
    except Exception as e:
        print(f"Error adding directory: {e}")
        return False

def remove_item(iso_path, is_dir=False):
    if not _state['is_loaded']: return False
    iso_obj = _state['iso']
    try:
        kwargs = {}
        if iso_obj.has_joliet(): kwargs['joliet_path'] = iso_path
        if iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = iso_path
        kwargs['iso_path'] = iso_path
        
        if is_dir:
            iso_obj.rm_directory(**kwargs)
        else:
            iso_obj.rm_file(**kwargs)
        return True
    except Exception as e:
        print(f"Error removing item: {e}")
        return False

def get_state():
    return _state
