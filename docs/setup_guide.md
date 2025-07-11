# Setup Guide for StatChat

This document provides a guide for setting up the StatChat project on both Mac and Windows systems.
The key steps include creating a virtual environment, installing dependencies, and configuring the project for development.

## Step 1: Clone StatChat

If you haven't already, clone the StatChat repository from GitHub.
This will download the project files to your local machine.
Make sure you have Git installed on your system.
If you don't have it, you can download it from [git-scm.com](https://git-scm.com/).

```shell
git clone https://github.com/datasciencecampus/statschat-global.git
cd statschat-global
```

## Step 2a: Installation on Mac

The project requires specific versions of some packages so it is recommended to
set up a virtual environment.  Using venv and pip:

   ```shell
   python3.11 -m venv env
   source env/bin/activate

   python -m pip install --upgrade pip
   python -m pip install .
   ```

> [!NOTE]
> If you are doing development work on `statschat-global`, you should install the
> package locally as editable with our optional `dev` dependencies:
>
> ```shell
> python -m pip install -e ".[dev]"
> ```

## Step 2b: Installation on Windows

The project requires specific versions of some packages so it is recommended to
set up a virtual environment.

Before you download the `statschat-global` repo you should have the following:

- Python (version 3.11)

For now, we can only guarantee the project will work with Python 3.11.

### Getting Python

In order to get the relevant Python version (3.11.10 is the assumed version),
you will need to have the Anaconda Navigator installed. Alternatively you can
use [miniconda](https://docs.anaconda.com/miniconda/).

Once this is installed, you can then launch the PowerShell Prompt.
Use the following command to create a new python environment with Python 3.11:

   ```bash
   conda create --name statchat_dev python=3.11
   ```

This will create a new virtual environment whose name is statchat_dev.
If the new environment hasn't auto activated, run the following:

   ```bash
   conda activate statchat_dev
   ```

This will activate the statchat_dev virtual environment.
You can also use this to switch back to the statchat_dev environment if you have switched to another.

Check that you have the correct python version (currently 3.11.10) by running the following.

   ```bash
   python --version
   ```

If you have anything below 3.10 or equal or greater than 3.12 then the project may have issues.
If this is the case, please re-create the virtual environment ensuring that the python version is specified.

## Step 3: Installing statchat

The codebase is meant to also run as a python library, in order to install this
you will then need to run:

   ```bash
   pip install --upgrade pip
   pip install .
   ```

> [!NOTE]
> If you are doing development work on `statschat`, you should install the
> package locally as editable with our optional `dev` dependencies:
>
> ```shell
> pip install -e .
> ```

## Step 4: Set-Up Pre-commit Actions

This repository contains a configuration of pre-commit hooks. These are
language agnostic and focussed on repository security (such as detection of
passwords and API keys).

If approaching this project as a developer, you are encouraged to install and
enable `pre-commits` by running the following in your shell:

1. Install `pre-commit`:

   ```shell
   pip install pre-commit
   ```

2. Enable `pre-commit`:

   ```shell
   pre-commit install
   ```

Once pre-commits are activated, whenever you commit to this repository a series of checks will be executed.
The use of active pre-commits are highly encouraged.
If any of the hooks fail, the commit will be aborted, and you will need to fix the issues before trying again.

You can also run the pre-commit hooks manually using the following command:

   ```shell
   pre-commit run --all-files
   ```

This command runs all the pre-commit hooks on all the files in the repository,
allowing you to check your code before committing.

By following these steps, you can ensure that your development environment is set up to use the pre-commit hooks,
helping to maintain a clean and consistent codebase.

> [!NOTE]
> Pre-commit hooks execute Python, so it expects a working Python build.

## Step 5: Set-Up Environment Variables

At this point, you will need to set up the environment variables required for the StatChat project.
This will likely include API keys, for interaction with the HuggingFace endpoints.
In order to do this, you will need to create a `.env` file in the root of the project directory.
This file should contain the following variables:

```plaintext
HF_TOKEN = "your_huggingface_token"
HOME_PATH = "/path/to/your/project/directory"
```

In order to get your HuggingFace token, you will need to create an account on [HuggingFace](https://huggingface.co/).
Once you have created an account, you can generate a token by going to your account settings and
clicking on "Access Tokens".

## Step 6: Running the Tool

You are now ready to run the StatChat tool.
You can run the tool using the command line interface (CLI), through the API or the Flask web interface.
For more information on how to run the tool, please refer to the [Running StatChat](docs/running_statschat.md) documentation.

## Step 7: Additional Configuration

You may need to configure additional settings for the StatChat project.
This can include setting up environment variables, configuring the API keys, or adjusting the project settings.
For more information on how to configure the project, please refer to the [Configuration Guide](docs/config_guide.md).
