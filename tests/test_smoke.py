from sika_x.config import load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("TIMEZONE", raising=False)

    settings = load_settings(use_dotenv=False)

    assert settings.app_env == "dev"
    assert settings.timezone == "Africa/Accra"
    assert settings.database_url.startswith("sqlite:")


def test_load_settings_from_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")

    settings = load_settings(use_dotenv=False)

    assert settings.app_env == "staging"
