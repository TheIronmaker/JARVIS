

def info(info, method="text"):
    if method == "text":
        print(info)
    else:
        print(info) # TODO: send to window instead

def warning(info, method="text"):
    if method == "text":
        print("WARNING:", info)
    else:
        print(info) # TODO: send to window instead

def error(info, method="text"):
    if method == "text":
        print("ERROR:", info)
    else:
        print(info) # TODO: send to window instead