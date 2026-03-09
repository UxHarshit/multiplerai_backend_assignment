from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from app.dependencies import get_current_user
import asyncio
import traceback
import io
import shutil

router = APIRouter()


def _find_chrome() -> str:
    """Return the path to the Chrome / Chromium binary."""
    import os
    # Common Windows locations
    for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        base = os.environ.get(env)
        if not base:
            continue
        for rel in (
            r"Google\Chrome\Application\chrome.exe",
            r"Chromium\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe",
        ):
            p = os.path.join(base, rel)
            if os.path.isfile(p):
                return p
    # Fallback: search PATH
    p = shutil.which("chrome") or shutil.which("chromium")
    if p:
        return p
    raise FileNotFoundError(
        "Chrome/Chromium not found. Install Google Chrome or set its path."
    )


class ScreenshotRequest(BaseModel):
    url: str
    full_page: bool = False
    width: int = 1280
    height: int = 800


def _uc_capture(url: str, width: int, height: int, full_page: bool) -> bytes:
    import undetected_chromedriver as uc
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from PIL import Image

    options = uc.ChromeOptions()
    options.binary_location = _find_chrome()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--lang=en-US,en")
    options.add_argument("--disable-http2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = uc.Chrome(options=options, use_subprocess=True)
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)

        # wait for body
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(("tag name", "body"))
        )

        if full_page:
            # expand viewport to full page height
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(width, total_height)

        png_bytes = driver.get_screenshot_as_png()
    finally:
        driver.quit()

    # convert PNG → JPEG
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def _uc_health() -> str:
    import undetected_chromedriver as uc

    options = uc.ChromeOptions()
    options.binary_location = _find_chrome()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = uc.Chrome(options=options, use_subprocess=True)
    try:
        version = driver.capabilities.get("browserVersion", "unknown")
    finally:
        driver.quit()
    return version


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/")
async def take_screenshot(
    body: ScreenshotRequest,
    current_user: dict = Depends(get_current_user),
):
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"[screenshot] Capturing: {url}")

    try:
        screenshot_bytes = await asyncio.to_thread(
            _uc_capture, url, body.width, body.height, body.full_page
        )
        print(f"[screenshot] ✅ {len(screenshot_bytes)} bytes")
        return Response(
            content=screenshot_bytes,
            media_type="image/jpeg",
            headers={"X-Captured-URL": url},
        )

    except Exception as e:
        print(f"[screenshot] ❌ {traceback.format_exc()}")
        msg = str(e)
        if "timed out" in msg.lower() or "Timeout" in msg:
            detail = f"Timed out loading {url} — site may be blocking headless browsers."
        elif "net::ERR" in msg:
            detail = f"Network error: {msg}"
        else:
            detail = f"Screenshot failed: {msg}"
        raise HTTPException(status_code=500, detail=detail)


@router.get("/health")
async def screenshot_health():
    try:
        version = await asyncio.to_thread(_uc_health)
        return {"status": "ok", "chrome_version": version}
    except Exception as e:
        return {"status": "error", "detail": str(e)}



# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/")
async def take_screenshot(
    body: ScreenshotRequest,
    current_user: dict = Depends(get_current_user),
):
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"[screenshot] Capturing: {url}")

    try:
        screenshot_bytes = await _async_capture(url, body.width, body.height, body.full_page)
        print(f"[screenshot] ✅ {len(screenshot_bytes)} bytes")
        return Response(
            content=screenshot_bytes,
            media_type="image/jpeg",
            headers={"X-Captured-URL": url},
        )

    except Exception as e:
        print(f"[screenshot] ❌ {traceback.format_exc()}")
        msg = str(e)
        if "Executable doesn't exist" in msg or "chromium" in msg.lower():
            detail = "Chromium not found — run: playwright install chromium"
        elif "timed out" in msg.lower() or "Timeout" in msg:
            detail = f"Timed out loading {url} — site may be blocking headless browsers."
        elif "net::ERR" in msg:
            detail = f"Network error: {msg}"
        else:
            detail = f"Screenshot failed: {msg}"
        raise HTTPException(status_code=500, detail=detail)


@router.get("/health")
async def screenshot_health():
    try:
        version = await _async_health()
        return {"status": "ok", "chromium_version": version}
    except Exception as e:
        return {"status": "error", "detail": str(e)}