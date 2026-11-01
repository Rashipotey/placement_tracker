"""Browser end-to-end tests (Selenium + Edge/Chrome).

Opt-in: set E2E=1. Starts uvicorn (:8000) and the Vite dev server (:5173) and
stops them afterwards. Uses the configured DATABASE_URL; all records carry the
unique PREFIX and are removed by the session cleanup in tests/conftest.py.
"""
import os
import subprocess
import sys
import time
import uuid
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

if not os.environ.get("E2E"):
    pytest.skip("set E2E=1 to run browser tests", allow_module_level=True)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from tests.conftest import PREFIX

ROOT = Path(__file__).resolve().parents[2]
API = "http://localhost:8000"
WEB = "http://localhost:5173"


def _wait_http(url, seconds=60):
    end = time.time() + seconds
    while time.time() < end:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"{url} did not start")


def _port_free(port):
    import socket
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture(scope="module")
def servers():
    assert _port_free(8000) and _port_free(5173), "ports 8000/5173 must be free"
    env = dict(os.environ)
    env.setdefault("JWT_SECRET_KEY", "test-only-secret")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    npm = "npm.cmd" if os.name == "nt" else "npm"
    web = subprocess.Popen(
        [npm, "run", "dev", "--", "--port", "5173", "--strictPort"],
        cwd=ROOT / "frontend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        _wait_http(API + "/")
        _wait_http(WEB + "/")
        yield
    finally:
        for p in (api, web):
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                p.terminate()


@pytest.fixture(scope="module")
def browser(servers):
    opts = webdriver.EdgeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    d = webdriver.Edge(options=opts)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture(scope="module")
def creds():
    return {"name": PREFIX + "e2e", "email": f"{PREFIX}e2e_{uuid.uuid4().hex[:6]}@example.com",
            "password": "password123"}


def wait(d, cond, t=10):
    return WebDriverWait(d, t).until(cond)


def text_present(d, txt):
    wait(d, EC.text_to_be_present_in_element((By.TAG_NAME, "body"), txt))


def path(d):
    return d.execute_script("return window.location.pathname")


def login(d, creds):
    d.get(WEB + "/login")
    d.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(creds["email"])
    d.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(creds["password"])
    d.find_element(By.XPATH, "//button[text()='Log In']").click()
    wait(d, lambda x: path(x) == "/applications")


def test_1_protected_route_redirects_when_unauthenticated(browser):
    browser.get(WEB + "/applications")
    wait(browser, lambda d: path(d) == "/login")
    text_present(browser, "Log in")


def test_2_register_then_login(browser, creds):
    d = browser
    d.get(WEB + "/register")
    d.find_element(By.XPATH, "//label[contains(.,'Name')]//input").send_keys(creds["name"])
    d.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(creds["email"])
    d.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(creds["password"])
    d.find_element(By.XPATH, "//button[text()='Create Account']").click()
    wait(d, lambda x: path(x) == "/login")
    login(d, creds)
    text_present(d, "User: " + creds["email"])
    assert d.execute_script("return localStorage.getItem('access_token')")


@pytest.fixture(scope="module")
def company(servers, creds, browser):
    """Created through the API with the prefix (removed by session cleanup)."""
    import json
    def call(method, p, body=None, token=None):
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = "Bearer " + token
        r = urllib.request.Request(API + p, method=method, headers=h,
                                   data=json.dumps(body).encode() if body is not None else None)
        return json.loads(urllib.request.urlopen(r).read().decode())
    tok = call("POST", "/auth/login?" + urllib.parse.urlencode(
        {"email": creds["email"], "password": creds["password"]}))["access_token"]
    return call("POST", "/companies", {"name": PREFIX + "E2ECo", "role": "Intern"}, tok)


def rows(d):
    return d.find_elements(By.CSS_SELECTOR, "tbody tr")


def test_3_create_application_and_list(browser, creds, company):
    d = browser
    d.get(WEB + "/applications")
    text_present(d, "You have no applications yet")
    d.find_element(By.XPATH, "//button[text()='+ New']").click()
    wait(d, lambda x: path(x) == "/applications/new")
    wait(d, lambda x: len(Select(x.find_elements(By.TAG_NAME, "select")[0]).options) > 1)
    Select(d.find_elements(By.TAG_NAME, "select")[0]).select_by_value(company["id"])
    d.find_element(By.TAG_NAME, "textarea").send_keys("first note")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: path(x) == "/applications")
    wait(d, lambda x: len(rows(x)) == 1)
    assert PREFIX + "E2ECo" in rows(d)[0].text and "APPLIED" in rows(d)[0].text


def test_4_edit_application_and_filter(browser, company):
    d = browser
    rows(d)[0].find_element(By.LINK_TEXT, "Edit").click()
    wait(d, lambda x: "/edit" in path(x))
    wait(d, lambda x: x.find_element(By.TAG_NAME, "textarea").get_attribute("value") == "first note")
    Select(d.find_elements(By.TAG_NAME, "select")[1]).select_by_value("OFFER")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: path(x) == "/applications")
    wait(d, lambda x: len(rows(x)) == 1 and "OFFER" in rows(x)[0].text)

    sel = Select(d.find_element(By.TAG_NAME, "select"))
    sel.select_by_value("REJECTED")
    text_present(d, "You have no applications yet")
    sel = Select(d.find_element(By.TAG_NAME, "select"))
    sel.select_by_value("OFFER")
    wait(d, lambda x: len(rows(x)) == 1)
    Select(d.find_element(By.TAG_NAME, "select")).select_by_value("")
    wait(d, lambda x: len(rows(x)) == 1)


def test_5_delete_with_confirmation(browser):
    d = browser
    rows(d)[0].find_element(By.XPATH, ".//button[text()='Delete']").click()
    dialog = wait(d, EC.visibility_of_element_located((By.CSS_SELECTOR, "[role=dialog]")))
    assert "Confirm delete" in dialog.text
    dialog.find_element(By.XPATH, ".//button[text()='Cancel']").click()
    wait(d, EC.invisibility_of_element_located((By.CSS_SELECTOR, "[role=dialog]")))
    assert len(rows(d)) == 1  # cancel keeps the row
    rows(d)[0].find_element(By.XPATH, ".//button[text()='Delete']").click()
    d.find_element(By.CSS_SELECTOR, "[role=dialog]").find_element(By.XPATH, ".//button[text()='Delete']").click()
    text_present(d, "You have no applications yet")


def test_6_logout_then_protected_route_redirects(browser):
    d = browser
    d.find_element(By.XPATH, "//button[text()='Logout']").click()
    wait(d, lambda x: path(x) == "/login")
    assert d.execute_script("return localStorage.getItem('access_token')") is None
    d.get(WEB + "/applications")
    wait(d, lambda x: path(x) == "/login")


# ---- states and validation messages (Wireframes 2-5, LLD section 5) ----

def net(d, **cond):
    base = {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1}
    d.execute_cdp_cmd("Network.enable", {})
    d.execute_cdp_cmd("Network.emulateNetworkConditions", {**base, **cond})


def alert_text(d):
    return wait(d, EC.visibility_of_element_located((By.CSS_SELECTOR, "[role=alert]"))).text


def test_7_login_error_messages(browser, creds):
    d = browser
    d.get(WEB + "/login")
    d.find_element(By.XPATH, "//button[text()='Log In']").click()
    assert alert_text(d) == "Email is required"
    d.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(creds["email"])
    d.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys("wrong-password")
    d.find_element(By.XPATH, "//button[text()='Log In']").click()
    wait(d, lambda x: alert_text(x) == "Invalid email or password")


def test_8_register_validation_messages(browser, creds):
    d = browser
    d.get(WEB + "/register")
    d.find_element(By.XPATH, "//label[contains(.,'Name')]//input").send_keys(PREFIX + "v")
    d.find_element(By.XPATH, "//button[text()='Create Account']").click()
    assert alert_text(d) == "Email is required"
    d.find_element(By.CSS_SELECTOR, "input[type=email]").send_keys(creds["email"])
    d.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys("short")
    d.find_element(By.XPATH, "//button[text()='Create Account']").click()
    wait(d, lambda x: alert_text(x) == "Password must be at least 8 characters")
    pw = d.find_element(By.CSS_SELECTOR, "input[type=password]")
    pw.clear()
    pw.send_keys("password123")
    d.find_element(By.XPATH, "//button[text()='Create Account']").click()  # email already used
    wait(d, lambda x: alert_text(x) == "Email already registered")


def test_9_loading_and_error_states(browser, creds):
    d = browser
    login(d, creds)
    try:
        net(d, latency=3000)
        d.get(WEB + "/applications")
        text_present(d, "Loading applications...")
        net(d)
        wait(d, lambda x: "Loading applications..." not in x.find_element(By.TAG_NAME, "body").text, 15)

        d.get(WEB + "/applications")
        text_present(d, "You have no applications yet")
        net(d, offline=True)
        Select(d.find_element(By.TAG_NAME, "select")).select_by_value("OFFER")
        text_present(d, "Failed to load applications")
        retry = d.find_element(By.XPATH, "//button[text()='Retry']")
        net(d)
        retry.click()
        text_present(d, "You have no applications yet")
    finally:
        net(d)


def test_10_form_validation_and_save_error(browser, company):
    d = browser
    d.get(WEB + "/applications/new")
    wait(d, lambda x: len(Select(x.find_elements(By.TAG_NAME, "select")[0]).options) > 1)
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    assert alert_text(d) == "Company is required"
    Select(d.find_elements(By.TAG_NAME, "select")[0]).select_by_value(company["id"])
    try:
        net(d, offline=True)
        d.find_element(By.XPATH, "//button[text()='Save']").click()
        wait(d, lambda x: alert_text(x) == "Unable to save application")
    finally:
        net(d)
    d.find_element(By.XPATH, "//button[text()='Cancel']").click()
    wait(d, lambda x: path(x) == "/applications")
    text_present(d, "You have no applications yet")


def test_11_invalid_token_clears_and_redirects(browser):
    d = browser
    d.execute_script("localStorage.setItem('access_token', 'not-a-valid-jwt')")
    d.get(WEB + "/applications")
    wait(d, lambda x: path(x) == "/login")
    assert d.execute_script("return localStorage.getItem('access_token')") is None
