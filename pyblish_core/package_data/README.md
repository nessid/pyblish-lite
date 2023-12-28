# Pyblish Core

<img src="https://pyblish.readthedocs.io/en/latest/_images/logo_small.png" alt="Pyblish Logo" width="100">

## Overview
`pyblish_core` enhances the Pyblish ecosystem by providing advanced functionalities for plugin management, logging configuration, and pattern matching. It's designed to streamline workflows in digital content creation by offering tools for dynamic plugin registration, effective logging, and efficient string manipulation, tailored for various asset types and tasks.

## Features

- **Dynamic Plugin Management**: Automates the process of registering and deregistering Pyblish plugins based on specific project needs.
- **Advanced Logging Configuration**: Facilitates detailed logging in different contexts, aiding in debugging and monitoring.
- **Pattern Matching and String Manipulation**: Offers utilities to find, remove, or modify specific patterns in strings, enhancing data handling and processing.
- **Custom Plugin Collection**: Enables the creation of tailored plugin collections for specific asset types and tasks, improving workflow efficiency.
- **Data Generation for Plugins**: Supports the generation and management of plugin-related data, ensuring a more organized and efficient Pyblish workflow.


## Usage

### Filepath Tokens Updater

```python
from pyblish_core.tokens_updater import TokensUpdater

updater = TokensUpdater()
updater.register_plugins_by_task()
```

### Configure Logging

```python
from pyblish_core.logging_config import configure_logging

logger = configure_logging(__name__)
```

### Pattern Matching

```python
from pyblish_core.pattern_utils import find_pattern, remove_pattern

matches = find_pattern(input_string, pattern)
new_string = remove_pattern(input_string, pattern)
```

### Plugin Management

```python
from pyblish_core.plugins_collection import PluginsCollect
from pyblish_core.plugins_registration import PluginsRegister

plugins = PluginsCollect.from_asset_task(asset_type, task)
register = PluginsRegister(plugins)
register.register()
```


## License

`pyblish_core` is released under the [GNU GENERAL PUBLIC LICENSE](LICENSE).
