import shutil

def get_terminal_size():
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines

# Example usage
cols, rows = get_terminal_size()
print(f"Width: {cols}, Height: {rows}")