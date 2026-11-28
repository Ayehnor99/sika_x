from sika_x.config import Settings, load_settings


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


def test_settings_hides_api_key_in_repr():
    settings = Settings(
        app_env="dev",
        log_level="INFO",
        timezone="Africa/Accra",
        database_url="sqlite:///./sika_x.db",
        llm_provider="gemini",
        llm_model="gemini-4-hydrogen",
        llm_api_key="AIza-super-secret-do-not-leak",
    )
    assert "AIza-super-secret" not in repr(settings)
