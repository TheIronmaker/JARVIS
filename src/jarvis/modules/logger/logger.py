

class Logger:
    def info(message, method="text"):
        if method == "text":
            print(message)
        else:
            print(message) # TODO: send to window instead

    def warning(message, method="text"):
        if method == "text":
            print("WARNING:", message)
        else:
            print(message) # TODO: send to window instead

    def error(message, method="text"):
        if method == "text":
            print("ERROR:", message)
        else:
            print(message) # TODO: send to window instead