# README — Using `uv` in a Python Project

`uv` is a fast Python package and project manager. It can manage dependencies, lockfiles, Python versions, and project environments from a single tool.

In a standard project workflow, `uv` uses a virtual environment. By default, this environment is usually stored in a `.venv` directory at the root of the project.

---

## 1) Add a dependency

To add a project dependency:

```bash
uv add matplotlib
```
This updates:
- pyproject.toml
- the lockfile (uv.lock)
- the project's virtual environment

2) Add a development dependency

If the library is only needed for development, testing, notebooks, or utility scripts:
```bash
uv add --dev matplotlib
```

3) Remove a dependency
```bash
uv remove matplotlib
```
or 
```bash
uv remove --dev matplotlib
```

4) Update dependencies

Update one specific dependency:
```bash
uv lock --upgrade-package matplotlib
uv sync
```
5) Install / synchronize the project environment

To create the environment or bring it back in sync with pyproject.toml and uv.lock:
```bash
uv sync
```
In general, this is the command to run when:
- you have just cloned the project
- someone has modified the dependencies

6) Run a Python script with uv

```bash
uv run python my_script.py
```
uv run executes the command inside the project environment.