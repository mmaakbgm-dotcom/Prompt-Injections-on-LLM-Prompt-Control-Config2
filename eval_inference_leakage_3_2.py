import os, subprocess, sys, re

token = os.environ.get('GITHUB_TOKEN', '')
if not token:
    print("ERROR: GITHUB_TOKEN not found in environment")
    sys.exit(1)

print(f"GITHUB_TOKEN found (length={len(token)})")

push_url = f"https://{token}@github.com/mmaakbgm-dotcom/Prompt-Injections-on-LLM-Prompt-Control-Config2.git"
scrub = lambda s: re.sub(re.escape(token), "***", s) if s else ""

result = subprocess.run(
    ["git", "push", push_url, "main:main", "--set-upstream"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    capture_output=True, text=True, timeout=60
)

print(scrub(result.stdout))
print(scrub(result.stderr))

if result.returncode == 0:
    print("\nPUSH: SUCCESS")
    print("GitHub URL: https://github.com/mmaakbgm-dotcom/Prompt-Injections-on-LLM-Prompt-Control-Config2")
else:
    print("\nPUSH: FAILED")
    sys.exit(1)
