import re
import os

TARGET_FILE = os.path.join(os.path.dirname(__file__),"write_bash_submission_script.py")

def update_submission_script():
    if not os.path.exists(TARGET_FILE):
        print(f"Error: '{TARGET_FILE}' not found.")
        return

    with open(TARGET_FILE, "r") as f:
        content = f.read()

    print(f"Processing '{TARGET_FILE}'...\n")

    # 1. Replace REGISTERED=False with REGISTERED=True
    content, reg_count = re.subn(r'\bREGISTERED\s*=\s*False\b', 'REGISTERED=True', content)
    if reg_count > 0:
        print("Updated: REGISTERED=False -> REGISTERED=True")

    print("-" * 40)

    # 2. Match variables OR dict keys assigned to None
    # Group 1: The variable name or dict key (including quotes)
    # Group 2: Either an '=' or a ':'
    pattern = r'([\w"\']+)\s*([:=])\s*None'

    def ask_user_and_replace(match):
        identifier = match.group(1)  # e.g., default_modules or "M"
        operator = match.group(2)    # e.g., = or :
        
        # Strip quotes just for a cleaner terminal prompt
        display_name = identifier.strip('"\'')
        user_input = input(f"Enter value for '{display_name}': ")
        
        # Reconstruct the line preserving the correct operator (= or :)
        return f'{identifier} {operator} "{user_input}"'

    # Run the substitution
    updated_content = re.sub(pattern, ask_user_and_replace, content)

    with open(TARGET_FILE, "w") as f:
        f.write(updated_content)

    print("-" * 40)
    print(f"Success! '{TARGET_FILE}' has been updated.")

if __name__ == "__main__":
    update_submission_script()