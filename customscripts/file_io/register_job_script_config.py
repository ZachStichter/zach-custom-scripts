import re
import os

__provides__ = {
    'update_submission_script': 'update_submission_script'
}

TARGET_FILE = os.path.join(os.path.dirname(__file__), "write_bash_submission_script.py")

def update_submission_script():
    if not os.path.exists(TARGET_FILE):
        print(f"Error: '{TARGET_FILE}' not found.")
        return

    with open(TARGET_FILE, "r") as f:
        content = f.read()

    print(f"Processing '{TARGET_FILE}'...\n")

    # 1. Replace REGISTERED=False with REGISTERED=True (Global or top-level)
    content, reg_count = re.subn(r'\bREGISTERED\s*=\s*False\b', 'REGISTERED=True', content)
    if reg_count > 0:
        print("Updated: REGISTERED=False -> REGISTERED=True")

    print("-" * 40)

    # 2. Isolate the target function block
    # Group 1: The function header
    # Group 2: The body up until the next unindented line (\n\S) or end of file (\Z)
    func_pattern = r'(def default_bash_submission_script\s*\(\s*jobname\s*\)\s*:)(.*?(?=\n\S|\Z))'

    def process_function_scope(func_match):
        header = func_match.group(1)
        body = func_match.group(2)

        # Pattern for matching variables OR dict keys assigned to None
        none_pattern = r'([\w"\']+)\s*([:=])\s*None'

        def ask_user_and_replace(match):
            identifier = match.group(1)  # e.g., default_modules or "M"
            operator = match.group(2)    # e.g., = or :
            
            # Strip quotes for a cleaner terminal prompt
            display_name = identifier.strip('"\'')
            user_input = input(f"Enter value for '{display_name}': ")
            
            return f'{identifier} {operator} "{user_input}"'

        # Run substitution ONLY inside this function's body
        updated_body = re.sub(none_pattern, ask_user_and_replace, body)
        return header + updated_body

    # Apply the scoped replacement using re.DOTALL so '.' matches newlines
    updated_content, count = re.subn(func_pattern, process_function_scope, content, flags=re.DOTALL)

    if count == 0:
        print("Warning: 'def default_bash_submission_script(jobname):' function block not found.")
    else:
        with open(TARGET_FILE, "w") as f:
            f.write(updated_content)
        print("-" * 40)
        print(f"Success! '{TARGET_FILE}' has been updated safely.")

if __name__ == "__main__":
    update_submission_script()