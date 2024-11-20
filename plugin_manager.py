import os
import importlib.util

PLUGINS_DIR = "plugins"

class PluginSystem:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name, func):
        """Register a plugin by its name and function"""
        if name in self.plugins:
            print(f"Plugin '{name}' is already registered.")
        else:
            self.plugins[name] = func
            print(f"Plugin '{name}' registered successfully.")

    def run_plugin(self, name, **kwargs):
        """Execute a registered plugin by its name with options passed as kwargs."""
        if name in self.plugins:
            print(f"Running plugin '{name}' with options: {kwargs}")
            plugin_func = self.plugins[name]
            return plugin_func(**kwargs)
        else:
            print(f"Plugin '{name}' not found!")

def create_plugins_directory():
    """Create the plugins directory if it doesn't exist."""
    if not os.path.exists(PLUGINS_DIR):
        os.makedirs(PLUGINS_DIR)
        print("Plugins directory created.")

def create_plugin(name):
    """Create a new plugin with the given name."""
    sample_code = f"""
def run(options=None):
    print("Hello from the {name} plugin!")
    if options:
        print("Options provided:", options)
"""
    plugin_path = os.path.join(PLUGINS_DIR, f"{name}.py")
    with open(plugin_path, "w") as f:
        f.write(sample_code)
    print(f"Plugin '{name}' created. Edit it to add your functionality.")

def delete_plugin(name):
    """Delete a plugin with the given name."""
    plugin_path = os.path.join(PLUGINS_DIR, f"{name}.py")
    try:
        os.remove(plugin_path)
        print(f"Plugin '{name}' deleted.")
    except FileNotFoundError:
        print(f"Plugin '{name}' not found.")

def list_plugins():
    """List all plugins in the plugins directory."""
    plugins = [f[:-3] for f in os.listdir(PLUGINS_DIR) if f.endswith(".py")]
    print("Available plugins:", plugins)
    return plugins

def load_plugins(plugin_system, load_order=None, omit_files=None):
    """Load plugins into the PluginSystem."""
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            if omit_files and module_name in omit_files:
                continue

            # Use importlib to load the plugin module dynamically
            plugin_path = os.path.join(PLUGINS_DIR, filename)
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "run"):
                    plugin_system.register_plugin(module_name, module.run)
                print(f"Loaded plugin: {module_name}")
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")

def parse_options(options_input):
    """Parse user input options in key=value format."""
    options = {}
    if options_input:
        for opt in options_input.split(","):
            try:
                key, value = opt.split("=")
                options[key.strip()] = value.strip()
            except ValueError:
                print(f"Warning: Invalid option format '{opt}'. Expected key=value format.")
    return options

def main():
    create_plugins_directory()
    plugin_system = PluginSystem()
    
    while True:
        print("\nPlugin Manager")
        print("1. Create Plugin")
        print("2. Delete Plugin")
        print("3. List Plugins")
        print("4. Load and Run Plugins")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            name = input("Enter the plugin name: ").strip()
            if name:
                create_plugin(name)
        elif choice == "2":
            name = input("Enter the plugin name to delete: ").strip()
            if name:
                delete_plugin(name)
        elif choice == "3":
            list_plugins()
        elif choice == "4":
            load_order_input = input("Enter a comma-separated list of plugins to load in order (leave empty for default): ").strip()
            load_order = [x.strip() for x in load_order_input.split(",")] if load_order_input else None
            omit_files_input = input("Enter a comma-separated list of plugins to omit (leave empty for none): ").strip()
            omit_files = [x.strip() for x in omit_files_input.split(",")] if omit_files_input else None

            load_plugins(plugin_system, load_order=load_order, omit_files=omit_files)

            options_input = input("Enter options for plugins (in key=value format, comma-separated, e.g., 'task=greet,name=Alice'): ").strip()
            options = parse_options(options_input)

            for plugin_name in plugin_system.plugins.keys():
                plugin_system.run_plugin(plugin_name, **options)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
