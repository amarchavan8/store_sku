"""Command-line entry point."""

import os
import sys

from .orchestrator import process_event
from .reporting import is_new_event
from .tools import load_world_state

EVENTS_DIR = "events"


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)

    print("=" * 60)
    print("DISRUPTION RESPONDER")
    print("=" * 60)

    world = load_world_state.invoke({"path": "world_state.json"})

    force_all = "--all" in argv
    args = [a for a in argv if a != "--all"]

    if args:
        # explicit files passed -> always process them
        event_files = args
    else:
        all_files = sorted(
            os.path.join(EVENTS_DIR, f)
            for f in os.listdir(EVENTS_DIR)
            if f.endswith(".json")
        )
        event_files = all_files if force_all else [f for f in all_files if is_new_event(f)]

    if not event_files:
        print("\nNo new events to process. (Use --all to re-run everything.)")
        return

    for event_file in event_files:
        try:
            process_event(event_file, world)
        except Exception as e:
            print(f"\n[ERROR] failed on {event_file}: {e}")

    print(f"\nDone! Processed {len(event_files)} event(s).")


if __name__ == "__main__":
    main()
