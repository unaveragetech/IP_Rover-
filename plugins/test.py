def run(options=None):
    name = options.get("name", "Unknown")
    task = options.get("task", "do nothing")
    print(f"Hello, {name}! Ready to {task}.")
