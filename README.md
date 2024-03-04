# Key Features

- **Moving Average Calculation**: The application calculates moving averages in the translation event data.
- **Reading from JSONL Files**: Users can input translation events by providing JSONL (JSON Lines) files.
- **Write Results to File**: The application supports writing results to a file, developed in a scalable way to support different output sources in future versions.
- **User-Friendly CLI Interface**: Built with Poetry and Typer, the CLI provides a user-friendly interface for interacting with the application.

# How it works

The moving average algorithm processes translation events by:

1. Reading each event.
2. Checking if it fits the current window; if not, update the window until it does.
3. Registering the processed minute when the window changes.
4. Calculating the moving average based on events within the window.
5. Saving the current event statistics, for moving average calculation.
6. Repeating these steps for each event available in the input source.

# Getting started

### Creating and Activating the Virtual Environment

Before installing dependencies, create and activate the virtual environment using Poetry:

```
poetry shell
```

This command will create a virtual environment and automatically activate it for the current terminal session. All subsequent commands will run within this virtual environment.

### Installing Dependencies

Once inside the virtual environment, use Poetry to install the project dependencies:

```
poetry install
```

This command will install all the required dependencies specified in the pyproject.toml file, namely typer and pytest.

### Running the CLI Application

After installing the dependencies, you can run the CLI application using Poetry script. For example:

```
unbabel-cli --i ./resources/data.jsonl --w 10
```

### Additional Commands

This command:

```
unbabel-cli --help
```

will display the help message generated by Typer, providing details on how to use your CLI application effectively.

Additionally, you can run pytest to execute project tests:

```
pytest
```

This command will run all the test cases using pytest, helping ensure the correctness and reliability of the code.