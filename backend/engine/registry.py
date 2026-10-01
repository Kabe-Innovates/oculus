import importlib
import inspect
import logging
import pkgutil

import rules
from engine.base import FraudRule

logger = logging.getLogger(__name__)


class RuleRegistry:
    def __init__(self):
        self._rules = {}

    def register(self, rule: FraudRule):
        self._rules[rule.name] = rule

    def get_all(self):
        return list(self._rules.values())

    def discover(self):
        """Auto-discover FraudRule subclasses from the rules package.

        Skips abstract classes and classes not defined in the scanned module.
        A broken plugin logs an error but does not prevent other rules from loading.
        """
        package = rules
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"rules.{name}")
            except Exception:
                logger.exception("Failed to import rule module 'rules.%s'", name)
                continue

            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, FraudRule)
                    and item is not FraudRule
                    and not inspect.isabstract(item)
                    and item.__module__ == module.__name__
                ):
                    try:
                        self.register(item())
                    except Exception:
                        logger.exception("Failed to instantiate rule '%s'", item_name)
