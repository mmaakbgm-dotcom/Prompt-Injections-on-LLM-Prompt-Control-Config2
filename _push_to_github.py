import os, subprocess, sys, re

token = os.environ.get('GITHUB_TOKEN', '')
if not token:
    print("ERROR: GITHUB_TOKEN not found in environment")
    sys.exit(1)

print(f"Token found: YES (length={len(token)})")

push_url = f"https://{token}@github.com/mmaakbgm-dotcom/Prompt-Injections-on-LLM-Prompt-Control-Config2.git"

result = subprocess.run(
    ["git", "push", push_url, "main:main", "--set-upstream"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    capture_output=True, text=True, timeout=60
)

scrub = lambda s: re.sub(re.escape(token), "***", s)

if result.returncode == 0:
    print("PUSH: SUCCESS")
    if result.stderr:
        print(scrub(result.stderr))
else:
    print("PUSH: FAILED")
    print(scrub(result.stderr))
    print(scrub(result.stdout))
    sys.exit(1)
