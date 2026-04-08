from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.checker import VFSChecker
from app.models import (
    CheckResult,
    CheckStatus,
    City,
    SlotsResponse,
    StatusResponse,
    VFS_BOOKING_URL,
)
from app.scheduler import SlotMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_checker: VFSChecker | None = None
_monitor: SlotMonitor | None = None
_ws_clients: set[WebSocket] = set()


async def _broadcast(result: CheckResult) -> None:
    data = SlotsResponse(
        slots=result.slots,
        last_check=result.last_check,
        status=result.status,
    ).model_dump_json()

    dead: list[WebSocket] = []
    for ws in _ws_clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.discard(ws)


def _on_result(result: CheckResult) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_broadcast(result))
    except RuntimeError:
        pass


def create_app(start_checker: bool = True) -> FastAPI:
    global _checker, _monitor

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _checker, _monitor
        if start_checker:
            _checker = VFSChecker(headless=False)
            await _checker.start_browser()
            _monitor = SlotMonitor(checker=_checker, on_result=_on_result)
            await _monitor.start()
        else:
            _checker = VFSChecker(headless=True)
            _monitor = SlotMonitor(checker=_checker)
        yield
        if _monitor:
            await _monitor.stop()
        if _checker:
            await _checker.close()

    app = FastAPI(title="VFS Visa Slot Monitor", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/status")
    async def get_status() -> StatusResponse:
        result = _checker.result if _checker else CheckResult()
        return StatusResponse(
            status=result.status,
            last_check=result.last_check,
            error_message=result.error_message,
            is_monitoring=_monitor.is_running if _monitor else False,
        )

    @app.get("/api/slots")
    async def get_all_slots() -> SlotsResponse:
        result = _checker.result if _checker else CheckResult()
        return SlotsResponse(
            slots=result.slots,
            last_check=result.last_check,
            status=result.status,
        )

    @app.get("/api/slots/{city}")
    async def get_slots_by_city(city: str) -> SlotsResponse:
        try:
            city_enum = City(city)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Неизвестный город: {city}. Допустимые: {[c.value for c in City]}",
            )
        result = _checker.result if _checker else CheckResult()
        filtered = result.slots_for_city(city_enum)
        return SlotsResponse(
            slots=filtered,
            last_check=result.last_check,
            status=result.status,
        )

    @app.get("/api/booking-url")
    async def get_booking_url():
        return {"url": VFS_BOOKING_URL}

    @app.post("/api/check-now")
    async def check_now() -> SlotsResponse:
        if not _checker:
            raise HTTPException(status_code=503, detail="Checker не инициализирован")
        result = await _checker.check_slots()
        return SlotsResponse(
            slots=result.slots,
            last_check=result.last_check,
            status=result.status,
        )

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await ws.accept()
        _ws_clients.add(ws)
        try:
            result = _checker.result if _checker else CheckResult()
            await ws.send_text(
                SlotsResponse(
                    slots=result.slots,
                    last_check=result.last_check,
                    status=result.status,
                ).model_dump_json()
            )
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            _ws_clients.discard(ws)

    static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app(start_checker=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
