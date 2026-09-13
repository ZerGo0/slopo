def handle_command(command):
    result = ""
    match command:
        case "quit":
            result = "exiting"
            return 0
        case "help":
            name = "help"
            result = f"showing {name}"
        case _:
            result = "unknown"
            return -1
    return result
