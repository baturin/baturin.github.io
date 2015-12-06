
def format_file_size(size):
    if size > 1024 * 1024:
        return "%.2fM" % (size / (1024.0 * 1024.0))
    if size > 1024:
        return "%.2fK" % (size / 1024.0)
    else:
        return size
