import hashlib
import sys
import os
import struct
import argparse

def apply_hex_patch(file, offset, old_value, new_value):
    old_value_no_space = old_value.replace(' ', '')
    new_value_no_space = new_value.replace(' ', '')

    old_value_len = len(old_value_no_space)
    new_value_len = len(new_value_no_space)
    
    if old_value_len != new_value_len or old_value_len % 2 != 0:
        print("Hex patch notation is malformed.")
        return False
    byte_len = old_value_len // 2
    
    old_value_bytes = bytearray.fromhex(old_value_no_space)
    new_value_bytes = bytearray.fromhex(new_value_no_space)
    
    with open(file, 'r+b') as f:
        f.seek(offset)
        actual_bytes = f.read(byte_len)
        
        # TODO: Change new to old
        if actual_bytes != new_value_bytes:
            print("Original bytes do not match the bytes in the file.")
            return False
            
        f.seek(offset)
        f.write(new_value_bytes)
    
    return True

    
def apply_int_patch(file, offset, old_value, new_value, byte_amount, is_signed):
    old_value_int_bytes = int(old_value).to_bytes(byte_amount, byteorder='little', signed=is_signed)
    new_value_int_bytes = int(new_value).to_bytes(byte_amount, byteorder='little', signed=is_signed)
    
    with open(file, 'r+b') as f:
        f.seek(offset)
        actual_bytes = f.read(byte_amount)
        
        # TODO: Change new to old
        if actual_bytes != new_value_int_bytes:
            print("Original bytes do not match the bytes in the file.")
            return False
            
        f.seek(offset)
        f.write(new_value_int_bytes)
    
    return True
    
def apply_float_patch(file, offset, old_value, new_value, is_single):
    struct_type = 'f' if is_single else 'd'
    byte_amount = 4 if is_single else 8
    old_value_float_bytes = struct.pack(struct_type, float(old_value))
    new_value_float_bytes = struct.pack(struct_type, float(new_value))
    
    with open(file, 'r+b') as f:
        f.seek(offset)
        actual_bytes = f.read(byte_amount)
        
        # TODO: Change new to old
        if actual_bytes != new_value_float_bytes:
            print("Original bytes do not match the bytes in the file.")
            return False
            
        f.seek(offset)
        f.write(new_value_float_bytes)
    
    return True
    
def find_file_in_folder(file_name, folder):
    for f in os.listdir(folder):
        abs_f = os.path.join(folder, f)
        if f == file_name and not os.path.isdir(abs_f):
            return abs_f
    return ''
    
def get_file_path(file_name, fl_dir):
    binary_dirs = ['EXE', 'DLLS\\BIN']
    
    for dir in binary_dirs:
        file_path = find_file_in_folder(file_name, os.path.join(fl_dir, dir))
        if file_path:
            return file_path
    return ''

def get_file_hash(file, hash):
    with open(file, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, hash).hexdigest()

def start():
    parser = argparse.ArgumentParser(
        prog='FLStaticPatch',
        description='Patches binary files based on a config.')
    parser.add_argument('config_file', help='Path to the config file.')
    parser.add_argument('freelancer_dir', help='Path to the Freelancer directory.')
    args = parser.parse_args()

    read_header = True
    file_path = None

    # TODO: Remove hardcoded path
    with open(args.config_file, 'r') as file:
        for line in file:
            clean_line = line.rstrip()
            
            if clean_line:
                if clean_line[0] == '#':
                    continue
                elif read_header:
                    # Parsing header
                    read_header = False
                    
                    header_split = clean_line.split(' ')
                    file_name = header_split[0]
                    file_hash = header_split[1].replace('.', '')
                    
                    file_path = get_file_path(file_name, args.freelancer_dir)
                    if not file_path:
                        print(f"Could not find file '{file_name}'.", file=sys.stderr)
                        return
                    
                    actual_file_hash = get_file_hash(file_path, 'sha1')
                    
                    # TODO: Change to not equals
                    if actual_file_hash == file_hash:
                        print(f"Hash for {file_path} does not match.", file=sys.stderr)
                        return
                else:
                    offset_split = clean_line.split(':', 1)
                    offset = offset_split[0]
                    offset_hex = int(f"0x{offset}", 16)
                    
                    type_split = offset_split[1].lstrip().split(' ', 1)
                    edit_type = type_split[0]
                    
                    patch_split = type_split[1].split('=', 1)[0].lstrip()
                    
                    patch_value_split = patch_split.split('->')
                    original_value = patch_value_split[0].strip()
                    new_value = patch_value_split[1].strip()
                    
                    patch_str = f"{edit_type} {original_value} -> {new_value} in file {file_path} at offset {hex(offset_hex)}"
                    
                    result = False
                    if edit_type == 'Hex':
                        result = apply_hex_patch(file_path, offset_hex, original_value, new_value)
                    elif 'Int' in edit_type:
                        is_signed = edit_type[0] != 'U'
                        byte_amount = int(edit_type.split('Int')[-1]) // 8
                        
                        result = apply_int_patch(file_path, offset_hex, original_value, new_value, byte_amount, is_signed)
                    elif 'Float' in edit_type:
                        is_single = edit_type.split('Float')[1] == '32'
                        result = apply_float_patch(file_path, offset_hex, original_value, new_value, is_single)
                    else:
                        print(f"Unknown patch type {edit_type}.", file=sys.stderr)


                    if not result:
                        print(f"Patch {patch_str} is invalid. See above.", file=sys.stderr)
                        return
                    else:
                        print(f"Applied patch {patch_str}")
                    
            else:
                read_header = True
            

if __name__ == "__main__":
    start()