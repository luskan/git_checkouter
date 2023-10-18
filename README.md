### Project Title
Git Branch by Date

### Brief Project Description
This Python script automates the process of finding the nearest Git commit based on a specified date and time, and then creates a new branch based on that commit. Useful for project rollbacks, audits, bisecting git history while debugging or exploring code state at a specific point in time.

### Installation Guide

#### Prerequisites
- Python 3.x
- Git

#### Steps
1. Clone this repository to your local machine.
    ```
    git clone https://github.com/luskan/git_checkouter.git
    ```
2. Navigate to the project folder.
    ```
    cd git_checkouter
    ```
3. Optionally, create a virtual environment.
    ```
    python3 -m venv venv
    ```
4. Activate the virtual environment.
    - On macOS and Linux:
        ```
        source venv/bin/activate
        ```
    - On Windows:
        ```
        .\venv\Scripts\activate
        ```
5. Run the script.
    ```
    python git_checkouter.py
    ```

### Usage Guide
Run the script and pass in the necessary command-line arguments. You can also modify the default variables within the script. 

As a precaution, remember to backup your repositories before using this script, as it will make changes to them.

#### Command-Line Options
- `--path`: Path to the folder containing Git repositories.
- `--date`: Target date and time in MM:DD:YYYY HH:MM format.
- `--timediff`: Minimum time difference in days.
- `--prefix`: Prefix for the new branch name. Default is 'tst_'
- `--delete`: Delete existing branches with the specified prefix (default is True).
  
#### Example
```bash
python main.py --path "/path/to/repos" --date "09:26:2023 23:00" --timediff 7 --prefix "tst_" --delete True
```

### Examples
- To find and branch from the nearest commit around September 26, 2023, 23:00 in repositories located at `/path/to/repos`:
    ```
    python main.py --path "/path/to/repos" --date "09:26:2023 23:00" --timediff 7
    ```
- To perform the above but in 'dry-run' mode without making actual changes:
    ```
    python main.py --path "/path/to/repos" --date "09:26:2023 23:00" --timediff 7 --dry-run True
    ```

### Credits
Marcin Jędrzejewski

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.