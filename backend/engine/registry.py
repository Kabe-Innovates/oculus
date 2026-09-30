import importlib
import pkgutil
import rules
from engine.base import FraudRule

class RuleRegistry:
    def __init__(self):
        self._rules = {}

    def register(self, rule: FraudRule):
        self._rules[rule.name] = rule

    def get_all(self):
        return list(self._rules.values())

    def discover(self):
        package = rules
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"rules.{name}")
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, type) and issubclass(item, FraudRule) and item is not FraudRule:
                    self.register(item())
