# game/event_bus.py
from collections import defaultdict
from typing import Callable, List, Dict, Any

class EventBus:
    """A centralized event bus for decoupled communication between systems."""
    def __init__(self):
        self.subscribers: Dict[Any, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Any, callback: Callable):
        """Subscribes a callback to an event type."""
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: Any, callback: Callable):
        """Unsubscribes a callback from an event type."""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
            except ValueError:
                # Callback not found, ignore silently.
                pass

    def publish(self, event_type: Any, **kwargs):
        """Publishes an event to all subscribers."""
        if event_type in self.subscribers:
            # Create a copy of the list to avoid issues if a subscriber modifies the list during iteration
            for callback in self.subscribers[event_type][:]:
                callback(**kwargs)