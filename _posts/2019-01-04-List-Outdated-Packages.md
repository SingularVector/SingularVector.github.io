---
title: "Python - List Outdated Packages"
excerpt: "How to list all outdated Python packages with Pip and how to upgrade them"
categories:

  - Python
  - Tips
tags:
  - Python
  - Pip
  - Pip Packages
  - Python3
last_modified_at: 2026-11-02
---

To list outdated packages for a particular Python environment, invoke pip through that environment's interpreter:

```bash
python -m pip list --outdated
```

Here `python` means the interpreter for your project, normally inside an activated virtual environment. Depending on your installation, use `python3` on macOS/Linux or `py -m pip` on Windows. Check the target environment if you are unsure:

```bash
python -m pip --version
```

The list shows installed and available versions. It does not mean every upgrade is compatible with your application or its dependency constraints.

To upgrade one package, for example `requests`:

```bash
python -m pip install --upgrade requests
python -m pip check
```

`pip check` detects incompatible or missing declared dependencies; run the application's own tests as well. If your project uses a lock file, update it through that project's dependency workflow so that other machines reproduce the change.

For a new project, create an isolated environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, create it with `py -m venv .venv` and activate it in PowerShell with `.venv\Scripts\Activate.ps1`.

Avoid `sudo pip` and blanket upgrades of the system Python environment. The original post recommended `pipdate` and incorrectly said it came installed on Windows; pip's built-in commands are sufficient for listing outdated packages and upgrading selected ones.

References: [pip list](https://pip.pypa.io/en/stable/cli/pip_list/), [pip install](https://pip.pypa.io/en/stable/cli/pip_install/) and the [Python Packaging guide to virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
