# promptfoo_provider.py
from clinic import authenticate, is_authenticated, customer_chat


def call_api(prompt, options, context):
    """
    Promptfoo Python provider entrypoint.
    Must return a dict with an 'output' key.
    """
    try:
        # Ensure we're authenticated for every run (Promptfoo calls this repeatedly)
        if not is_authenticated():
            authenticate("alice", "alice123")  # valid user in this app

        out = customer_chat(prompt)

        # Promptfoo expects a string output
        if not isinstance(out, str):
            out = str(out)

        return {"output": out}

    except Exception as e:
        return {"output": "", "error": str(e)}
