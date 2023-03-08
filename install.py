import argparse
import os
import subprocess

SHELL = os.environ['SHELL']


ENTITIES = {
    'brew': {
        'detect': {
            'command': ['brew', '--version']
        },
        'curl': {
            'url': 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh',
            'args': '-fsSL',
            'shell': '/bin/bash',
            'env': {'NONINTERACTIVE': '1'},
        },
    },
    'mas': {
        'detect': {
            'command': ['mas', 'version']
        },
        'brew': {
            'package': 'mas'
        }
    },
    'fd': {
        'detect': {
            'command': ['fd', '--version']
        },
        'brew': {
            'package': 'fd'
        },
    },
    'fzf': {
        'detect': {
            'command': ['fzf', '--version']
        },
        'brew': {
            'package': 'fzf'
        },
    },
    'nvm': {
        'detect': {
            'command': [SHELL, '--login', '-c', 'nvm --version']
        },
        'curl': {
            'url': 'https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh',
            'args': '-fsSL',
            'shell': '/bin/bash',
        },
    },
    'node': {
        'detect': {
            'command': ['node', '--version']
        },
        'nvm': {
            'version': '18.15.0'
        },
    },
    'golang': {
        'detect': {
            'command': ['go', 'version']
        },
        'pkg': {
            'url': 'https://go.dev/dl/go1.20.2.darwin-arm64.pkg'
        }
    },
    'rust': {
        'detect': {
            'command': ['rustc', '--version']
        },
        'curl': {
            'url': 'https://sh.rustup.rs',
            'args': "--proto '=https' --tlsv1.2 -sSf",
            'shell': '/bin/bash',
            'script_args': '-y'
        },
    },
    'tmux': {
        'detect': {
            'command': ['tmux', '-V']
        },
        'brew': {
            'package': 'tmux'
        },
    },
    'vim': {},
    'things': {
        'detect': {
            'command': "mas list | grep 904280696 | awk '{print $3;}'",
            'shell': True
        },
        'mas': {
            'app': '904280696'
        }
    },
    'obsidian': {},
    'chrome': {},
    'miniconda': {
        'detect': {
            'command': ['conda', '--version']
        },
        'run': {
            'command': """\
                curl -o /tmp/miniconda-installer.sh -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh \
                  && /bin/bash /tmp/miniconda-installer.sh -b \
                  && conda init zsh
            """
        }
    },
    'rosetta': {
        'detect': {
            'command': '/usr/bin/pgrep -q oahd && echo installed',
            'shell': True
        },
        'run': {
            'command': 'sudo /usr/sbin/softwareupdate --install-rosetta --agree-to-license',
            'require_sudo': True
        }
    },
    'aws-cli': {
        'detect': {
            'command': ['aws', '--version']
        },
        'pkg': {
            'url': 'https://awscli.amazonaws.com/AWSCLIV2.pkg'
        }
    },
    'github-cli': {
        'detect': {
            'command': ['gh', '--version']
        },
        'brew': {
            'package': 'gh'
        },
    },
    'defaultbrowser': {
        'detect': {
            'command': 'defaultbrowser > /dev/null && echo installed',
            'shell': True
        },
        'brew': {
            'package': 'defaultbrowser'
        },
    },
    'jq': {
        'detect': {
            'command': ['jq', '--version']
        },
        'brew': {
            'package': 'jq'
        },
    },
    'poetry': {
        'detect': {
            'command': ['poetry', '--version']
        },
        'curl': {
            'url': 'https://install.python-poetry.org',
            'args': '-fsSL',
            'shell': 'python3',
        },
    },
    'discord': {
        'dmg': {
            'url': 'https://discord.com/api/download?platform=osx'
        }
    },
    'docker': {
    },
}

def system(component, include_detected=False):
    def decorator(func):
        def wrapper():
            matching_entities = {
                pkg: v
                for pkg, v in ENTITIES.items()
                if (
                    component in v
                    and ('found' not in v['detect'] or include_detected)
                )
            }
            func(matching_entities)
        return wrapper
    return decorator

def check_sudo():
    process = subprocess.run(['sudo', '-v', '-n'], capture_output=True)
    return process.returncode == 0

@system('detect')
def detect(entities):
    for pkg, v in entities.items():
        component = v['detect']
        try:
            shell = component.get('shell', False)
            executable = component.get('executable', None)

            process = subprocess.run(
                component['command'], 
                shell=shell, 
                executable=executable,
                capture_output=True, 
                text=True
            )

            if process.returncode != 0:
                continue

            component['found'] = process.stdout.strip().split('\n')[0]
            print(f"found '{pkg}': '{component['found']}'")
        except FileNotFoundError:
            pass

@system('curl')
def curl(entities):
    for pkg, v in entities.items():
        component = v['curl']
        curl_cmdline = f"curl {component['args']} {component['url']}"

        if 'script_args' in component:
            script_args = f" -- {component['script_args']}"
        else:
            script_args = ''

        env = os.environ.copy()
        env.update(component.get('env', {}))

        subprocess.run(
            f"{component['shell']} -c \"$({curl_cmdline})\"{script_args}", 
            shell=True, 
            env=env,
            check=True
        )

@system('brew')
def brew(entities):
    if len(entities) == 0:
        return

    packages = [v['brew']['package'] for _, v in entities.items()]

    subprocess.run(
        f"brew install {' '.join(packages)}", 
        shell=True, 
        check=True
    )

@system('nvm')
def nvm(entities):
    for pkg, v in entities.items():
        component = v['nvm']

        subprocess.run(
            [SHELL, '--login', '-c', f"nvm install {component['version']}"],
            check=True
        )
        subprocess.run(
            [SHELL, '--login', '-c', f"nvm use {component['version']}"],
            check=True
        )

@system('run')
def run(entities):
    for pkg, v in entities.items():
        component = v['run']

        if component['require_sudo'] and not check_sudo():
            print('error: sudo required. run sudo then re-run.')
            exit(1)

        subprocess.run(
            component['command'],
            shell=True, 
            check=True
        )

@system('pkg')
def pkg(entities):
    for pkg, v in entities.items():
        component = v['pkg']

        if not check_sudo():
            print('error: sudo required. run sudo then re-run.')
            exit(1)

        subprocess.run(
            ['curl', '-fsSL', '-o', f"/tmp/{pkg}.pkg", component['url']],
            check=True
        )
        subprocess.run(
            ['sudo', 'installer', '-pkg', f"/tmp/{pkg}.pkg", '-target', '/'],
            check=True
        )

@system('mas')
def mas(entities):
    if len(entities) == 0:
        return

    apps = [v['mas']['app'] for _, v in entities.items()]

    subprocess.run(
        f"mas install {' '.join(apps)}", 
        shell=True, 
        check=True
    )


def main():
    parser = argparse.ArgumentParser(
        prog = 'install.py',
        description = 'Installs and configures my dev machines'
    )
    parser.add_argument('-n', '--dry-run', action='store_true')

    args = parser.parse_args()

    detect()
    curl()
    brew()
    nvm()
    run()
    pkg()
    mas()


if __name__ == '__main__':
    main()