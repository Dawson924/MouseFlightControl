import os
import sys

import yaml

I18N_DIR = './i18n'


def process_yaml_files(key, action):
    if not os.path.isdir(I18N_DIR):
        print(f'Error: Directory {I18N_DIR} does not exist!', file=sys.stderr)
        return False

    yml_files = [f for f in os.listdir(I18N_DIR) if f.endswith('.yml')]
    if not yml_files:
        print(f'Warning: No YAML files found in {I18N_DIR}', file=sys.stdout)
        return True

    for file_name in yml_files:
        file_path = os.path.join(I18N_DIR, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f'Error reading {file_name}: {e}', file=sys.stderr)
            return False

        if action == 'add':
            if key not in data:
                data[key] = ''
        elif action == 'del':
            if key in data:
                del data[key]
        elif action == 'rename':
            old_key, new_key = key
            if old_key not in data:
                print(
                    f"Warning: Key '{old_key}' not found in {file_name}",
                    file=sys.stdout,
                )
            else:
                value = data.pop(old_key)
                data[new_key] = value

        sorted_data = dict(sorted(data.items()))
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    sorted_data,
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                    default_flow_style=False,
                )
        except yaml.YAMLError as e:
            print(f'Error writing to {file_name}: {e}', file=sys.stderr)
            return False

    if action == 'add':
        print(f"Successfully added key '{key}' to all YAML files in {I18N_DIR}")
    elif action == 'del':
        print(f"Successfully removed key '{key}' from all YAML files in {I18N_DIR}")
    elif action == 'rename':
        old_key, new_key = key
        print(
            f"Successfully renamed key '{old_key}' to '{new_key}' in all YAML files in {I18N_DIR}"
        )
    return True


def main():
    print(
        "YAML Localization Manager - Use 'add <key>', 'del <key>', 'rename <old_key> <new_key>' to manage keys, 'exit' to quit"
    )
    while True:
        user_input = input('> ').strip()
        if not user_input:
            continue
        if user_input.lower() in ['exit', 'quit']:
            print('Exiting program...')
            sys.exit(0)

        parts = user_input.split(maxsplit=2)
        if len(parts) < 2:
            print(
                "Error: Invalid command. Use 'add <key>', 'del <key>', 'rename <old_key> <new_key>'",
                file=sys.stderr,
            )
            continue

        action = parts[0].lower()
        key = None
        if action in ['add', 'del']:
            key = parts[1]
            if ' ' in key:
                print('Error: Key cannot contain spaces!', file=sys.stderr)
                continue
        elif action in ['rename', 'ren']:
            if len(parts) < 3:
                print(
                    "Error: Invalid command. Use 'rename <old_key> <new_key>'",
                    file=sys.stderr,
                )
                continue
            old_key, new_key = parts[1], parts[2]
            if ' ' in old_key or ' ' in new_key:
                print(
                    'Error: Old key and new key cannot contain spaces!', file=sys.stderr
                )
                continue
            key = (old_key, new_key)
            action = 'rename'
        else:
            print(
                "Error: Invalid action. Only 'add', 'del', 'rename' (or 'ren') are allowed",
                file=sys.stderr,
            )
            continue

        process_yaml_files(key, action)


if __name__ == '__main__':
    main()
