import logging
import uuid

from fastapi import FastAPI, Request

from sika_x.api.routes_chat import router as chat_router
from sika_x.config import Settings, load_settings
from sika_x.db import init_db, make_engine, make_session_factory

logger = logging.getLogger("sika_x.api")


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    logging.basicConfig(
        level=getattr(logging, cfg.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    engine = make_engine(cfg.database_url)
    init_db(engine)

    app = FastAPI(title="sika_x", version="0.1.0")
    app.state.settings = cfg
    app.state.session_factory = make_session_factory(engine)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        logger.info(
            "request.start request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request.end request_id=%s status=%s",
            request_id,
            response.status_code,
        )
        return response

    app.include_router(chat_router)
    return app


app = create_app()
