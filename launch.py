import os
import subprocess
from threading import Thread, Lock
from itertools import cycle
import argparse
from lib.config import get_config
from termcolor import colored
import getpass

SUPERVISOR_CONF_FILENAME = 'supervisor.conf'
CONFIG_YAML_FILENAME = 'config.yaml'

# Color cycle for logs
colors = cycle([
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "dark_grey",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_magenta",
    "light_cyan"
])

# Dictionary to store colors by process alias
process_colors = {}
terminate_flag = False
lock = Lock()


# Function to log lines with color
def log_line(color, alias, line):
    with lock:
        logline = f"[{alias}]: {line}"
        text = colored(logline, color)
        print(text, end="")


# Function to generate Supervisor configuration file
def generate_supervisor_conf(output_filepath=SUPERVISOR_CONF_FILENAME):
    cwd = os.getcwd()
    log_dir = os.path.join(cwd, 'logs')
    config_filepath = os.path.join(cwd, CONFIG_YAML_FILENAME)
    config = get_config(filepath=config_filepath)

    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Create empty log files
    for process in config['process_list']:
        alias = process['alias']
        stdout_log = os.path.join(log_dir, f'{alias}_stdout.log')
        stderr_log = os.path.join(log_dir, f'{alias}_stderr.log')
        open(stdout_log, 'a').close()
        open(stderr_log, 'a').close()

    # Get current username
    current_user = getpass.getuser()

    # Supervisor section
    supervisord_section = f"""[supervisord]
logfile={log_dir}/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile={log_dir}/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200
"""

    # Program section
    program_template = """[program:{alias}]
command=/bin/bash -c '{command}'
directory={directory}
autostart=true
autorestart=true
stderr_logfile={log_dir}/{alias}_stderr.log
stdout_logfile={log_dir}/{alias}_stdout.log
environment={environment}
user={user}
"""

    program_configs = []
    for process in config['process_list']:
        alias = process['alias']
        run = process['run']
        workdir = os.path.abspath(run['workdir'])  # Use absolute path
        precmd = run.get('precmd', '')
        cmd = run['cmd']
        user = run.get('user', current_user)  # Use current username by default
        env_vars = run.get('env', {})
        environment = ','.join([f"{key}={value}" for key, value in env_vars.items()])

        # Create the full command
        commands = [precmd, cmd] if precmd else [cmd]  # Use precmd only if it's not empty
        full_command = ' && '.join(commands)

        program_config = program_template.format(
            alias=alias,
            command=full_command,
            directory=workdir,
            environment=environment,
            user=user,
            log_dir=log_dir  # Add the log directory path
        )
        program_configs.append(program_config)

    supervisord_config = supervisord_section + '\n'.join(program_configs)

    output_filepath = os.path.join(os.getcwd(), output_filepath)
    with open(output_filepath, 'w') as file:
        file.write(supervisord_config)

    print(f"Supervisor configuration file successfully generated: {output_filepath}")


# Function to execute the dev command
def dev():
    cwd = os.getcwd()
    config = get_config(filepath=os.path.join(cwd, CONFIG_YAML_FILENAME))
    processes = config['process_list']

    control_threads = []

    for process in processes:
        alias = process['alias']
        run = process['run']
        env = run.get('env', {})
        workdir = run.get('workdir', '')
        precmd = run.get('precmd', '')
        cmd = run['cmd']
        color = next(colors)
        process_colors[alias] = color  # Assign color to the alias

        def watch_pipe(pipe, alias):
            for line in iter(pipe.readline, ''):
                log_line(process_colors[alias], alias, line)
            pipe.close()

        workingdir = os.path.join(cwd, workdir)
        commands = [item for item in (precmd, cmd) if item]
        command = ' && '.join(commands)

        process = subprocess.Popen(
            command,
            shell=True,
            cwd=workingdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=0,
            env={**os.environ, **env}  # Combine current environment with process-specific environment
        )
        thread = Thread(target=watch_pipe, args=(process.stdout, alias))
        thread.start()
        control_threads.append(thread)

    # Joining all threads before stopping
    for t in control_threads:
        t.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command management for the script.')
    subparsers = parser.add_subparsers(dest='command', help='Available subcommands')

    parser_supervisor_conf = subparsers.add_parser('supervisor_conf', help='Generate a Supervisor configuration file.')
    parser_supervisor_conf.add_argument('output', type=str, nargs='?', default=SUPERVISOR_CONF_FILENAME, help=f'Output path for the Supervisor configuration file (default: {SUPERVISOR_CONF_FILENAME}).')

    parser_dev = subparsers.add_parser('dev', help='Execute the dev command.')

    args = parser.parse_args()

    print(f"Command executed: {args.command}")

    if args.command == 'supervisor_conf':
        print(f"Generating Supervisor configuration file: {args.output}")
        generate_supervisor_conf(args.output)
    elif args.command == 'dev':
        print("Executing dev command.")
        dev()
