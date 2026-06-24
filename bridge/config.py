# Placeholder config module - replace with your actual config implementation
class AppConfig:
    _config = {}
    
    @staticmethod
    def load(path):
        import json
        try:
            with open(path, 'r') as f:
                AppConfig._config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            AppConfig._config = {}
        return AppConfig
    
    @staticmethod
    def path_value(key, default=None):
        keys = key.split(".")
        val = AppConfig._config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default
