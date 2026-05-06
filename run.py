"""Convenience entrypoint so old commands still work:

    python run.py
    python run.py --all
    python run.py events/foo.json

You can also use:
    python -m disruption_responder
"""

from disruption_responder.cli import main

if __name__ == "__main__":
    main()
