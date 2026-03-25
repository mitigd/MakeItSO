import pycdlib
import os
from datetime import datetime

# Global state for the ISO
_state = {
    'iso': None,
    'path': None,
    'current_dir': '/',
    'is_loaded': False,
    'back_stack': [],
    'forward_stack': []
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
            
            # Extract actual modification time robustly
            try:
                dt = entry.date
                year = 1900 + dt.years_since_1900
                modified_str = f"{year:04}-{dt.month:02}-{dt.day_of_month:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}"
            except Exception:
                modified_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            items.append({
                'name': name,
                'is_dir': entry.is_dir(),
                'size': entry.data_length,
                'modified': modified_str
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

def get_dir_tree(path='/'):
    """Return a flat list of all directory paths in the ISO."""
    if not _state['is_loaded']: return []
    
    dirs = ['/']
    iso_obj = _state['iso']
    
    def walk(p):
        try:
            kwargs = {}
            if iso_obj.has_joliet(): kwargs['joliet_path'] = p
            elif iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = p
            else: kwargs['iso_path'] = p
            
            for entry in iso_obj.list_children(**kwargs):
                if entry.is_dir() and not entry.is_dot() and not entry.is_dotdot():
                    null_char = '\x00'
                    ident = entry.file_identifier().decode('utf-16be' if iso_obj.has_joliet() else 'utf-8').replace(null_char, '')
                    full_path = f"{p.rstrip('/')}/{ident}".split(';')[0]
                    dirs.append(full_path)
                    walk(full_path)
        except: pass
        
    walk('/')
    return sorted(list(set(dirs)))

def extract_item(iso_path, local_dest):
    """Extract a single file (simplified) to a local path."""
    if not _state['is_loaded']: return False
    iso_obj = _state['iso']
    try:
        kwargs = {}
        if iso_obj.has_joliet(): kwargs['joliet_path'] = iso_path
        elif iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = iso_path
        else: kwargs['iso_path'] = iso_path
        
        iso_obj.get_file_from_iso(local_dest, **kwargs)
        return True
    except Exception as e:
        print(f"Error extracting {iso_path}: {e}")
        return False

def extract_all(dest_dir, progress_callback=None):
    """Recursively extract all files with optional progress callback."""
    if not _state['is_loaded']: return False
    iso_obj = _state['iso']
    
    # Pre-count files for progress if possible
    # (Simplified: we'll just emit progress per file)
    
    def extract_walk(p):
        try:
            kwargs = {}
            if iso_obj.has_joliet(): kwargs['joliet_path'] = p
            elif iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = p
            else: kwargs['iso_path'] = p
            
            items = list(iso_obj.list_children(**kwargs))
            for entry in items:
                if entry.is_dot() or entry.is_dotdot(): continue
                
                null_char = '\x00'
                name = entry.file_identifier().decode('utf-16be' if iso_obj.has_joliet() else 'utf-8').replace(null_char, '').split(';')[0]
                
                rel_path = f"{p.rstrip('/')}/{name}"
                local_path = os.path.join(dest_dir, rel_path.lstrip('/'))
                
                if entry.is_dir():
                    os.makedirs(local_path, exist_ok=True)
                    extract_walk(rel_path)
                else:
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    extract_item(rel_path, local_path)
                    if progress_callback:
                        progress_callback(name)
        except: pass
        
    extract_walk('/')
    return True

def set_current_dir(path, push_history=True):
    if not _state['is_loaded']: return
    if push_history and path != _state['current_dir']:
        _state['back_stack'].append(_state['current_dir'])
        _state['forward_stack'].clear()
    _state['current_dir'] = path

def go_up():
    if not _state['is_loaded']: return
    if _state['current_dir'] == '/': return
    
    parts = _state['current_dir'].rstrip('/').split('/')
    new_path = '/'
    if len(parts) > 1:
        new_path = '/'.join(parts[:-1])
    
    set_current_dir(new_path)

def go_back():
    if not _state['back_stack']: return
    _state['forward_stack'].append(_state['current_dir'])
    _state['current_dir'] = _state['back_stack'].pop()

def go_forward():
    if not _state['forward_stack']: return
    _state['back_stack'].append(_state['current_dir'])
    _state['current_dir'] = _state['forward_stack'].pop()

def get_state():
    return _state

def get_total_size():
    """Calculate the total size of all files in the ISO."""
    if not _state['is_loaded']: return 0
    iso_obj = _state['iso']
    
    # Baseline from disk if it's a known file (catches 360/multi-session sizes)
    disk_size = 0
    if _state['path'] and os.path.exists(_state['path']):
        disk_size = os.path.getsize(_state['path'])
        
    walker_total = 0
    def walk(p):
        nonlocal walker_total
        try:
            kwargs = {}
            if iso_obj.has_joliet(): kwargs['joliet_path'] = p
            elif iso_obj.has_rock_ridge(): kwargs['rock_ridge_path'] = p
            else: kwargs['iso_path'] = p
            
            for entry in iso_obj.list_children(**kwargs):
                if entry.is_dot() or entry.is_dotdot(): continue
                if entry.is_dir():
                    name = None
                    if iso_obj.has_joliet():
                        try: name = entry.file_identifier().decode('utf-16be').replace('\x00', '')
                        except: pass
                    if not name:
                        name = entry.file_identifier().decode('utf-8', errors='replace')
                    if ';' in name: name = name.split(';')[0]
                    walk(f"{p.rstrip('/')}/{name}")
                else:
                    walker_total += entry.data_length
        except: pass
        
    walk('/')
    # Return the larger of the two (handles hidden partitions vs new additions)
    return max(disk_size, walker_total)
