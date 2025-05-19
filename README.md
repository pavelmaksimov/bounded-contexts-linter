# Bounded Contexts Linter

A static code analyzer that checks the isolation of bounded contexts in Domain-Driven Design (DDD) projects. 
This linter ensures that dependencies between modules occur only within a single bounded context, 
helping to maintain proper isolation between different domains in your application.

## Overview

In Domain-Driven Design, bounded contexts are a central pattern that helps in dealing with large models by dividing 
them into different contexts with explicit boundaries. This linter helps enforce these boundaries by:

1. Checking that modules don't belong to multiple bounded contexts
2. Verifying that imports between modules respect bounded context isolation

The linter recognizes two special contexts by default:
- **sharedkernel**: Contains modules that can be imported by any context
- **sharedscope**: Contains interfaces for interaction between contexts that can be safely imported

See the details of the work on the examples below.

## Installation

### Requirements
- Python 3.11 or higher

### Install from PyPI
```bash
pip install bounded-contexts-linter
```

### Install with flake8 integration
```bash
pip install bounded-contexts-linter[flake8]
```

## Usage

### Command Line Interface

Run the linter on your project:

```bash
bc-linter /path/to/your/project [/path/to/bounded-contexts.toml]
bounded-contexts-linter /path/to/your/project [/path/to/bounded-contexts.toml]
```

If the configuration file path is not provided, the linter will look for `bounded-contexts.toml` in the current working directory.

### Flake8 Integration

If you've installed the linter with flake8 integration, you can use it as a flake8 plugin:

```bash
flake8 /path/to/your/project
```

Make sure to configure flake8 to use the plugin by adding the following to your `.flake8` file:

```
[flake8]
enable-extensions = BC
```

## Configuration

The linter uses a TOML configuration file to define bounded contexts and their module patterns. By default, 
it looks for `bounded-contexts.toml` in the current working directory.

### Example Configuration

```toml
[bounded-contexts]
names = ["sharedkernel", "sharedscope", "sales", "crm", "user"]

[bounded-contexts.sharedkernel]
description = "Shared kernel modules that can be imported by any context"
contains = [
    "project.domains.user.*",
]

[bounded-contexts.sharedscope]
description = "Interface modules for interaction between contexts"
contains = [
    "project.domains.*.port",
]

[bounded-contexts.crm]
description = "Customer Relationship Management context"
contains = [
    "project.domains.crm.models",
    "project.domains.crm.services",
]

[bounded-contexts.sales]
description = "Sales context"
contains = [
    "project.domains.sales.models",
    "project.domains.sales.services",
]
```

### Pattern Syntax

The `contains` field in each bounded context section accepts a list of patterns that define which modules belong to that context. 
The pattern syntax supports:

- Exact module names: `project.domains.crm.models`
- Wildcards: `project.domains.crm.*`
- Multiple wildcards: `*.crm.*`

Examples:
- `project.utils` - Matches exactly the module named "project.utils"
- `project.domains.crm.*` - Matches all modules under "project.domains.crm"
- `project.domains.*.models` - Matches all modules starting with "project.domains." and ending ".models"
- `*.crm.*` - Matches all modules containing ".crm."

## How It Works

The linter performs the following checks:

1. **Overlapping Modules Check**: Ensures that no module belongs to multiple bounded contexts (except for sharedkernel and sharedscope)
2. **Import Isolation Check**: Ensures that modules from one bounded context don't import modules from another bounded context (except for sharedkernel and sharedscope)

The linter searches for modules in the specified project directory and checks their imports against the bounded contexts defined in the configuration file.
