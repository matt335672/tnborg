# Production scripts

| file            | purpose |
| -----           | ------- |
| daily.py        | Runs `backup.py`, `check.py` and `remote_sync.py` as appropriate, and emails the result to the sysadmin |
| backup.py       | Creates new borg archives for configured repositories |
| check.py        | Runs a `borg check` on configured repositories |
| remote_sync.py  | Calls `rclone` for each configured repository |

# Utility scripts
| file            | purpose |
| -----           | ------- |
| create_repos.py | Initial command to create borg repos for backups |
| rclone.py       | Shell command to run `rclone` from the command line |
| test_email.py   | Tests the SMTP reporting mechanism is working correctly |
