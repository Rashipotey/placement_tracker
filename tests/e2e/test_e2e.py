"""Browser end-to-end tests (Selenium + Edge/Chrome).

Opt-in: set E2E=1. Starts uvicorn (E2E_API_PORT, default 8000) and the Vite dev
server (E2E_WEB_PORT, default 5173) and stops them afterwards. Uses the configured DATABASE_URL; all records carry the
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
API_PORT = int(os.environ.get("E2E_API_PORT", "8000"))
WEB_PORT = int(os.environ.get("E2E_WEB_PORT", "5173"))
API = f"http://localhost:{API_PORT}"
WEB = f"http://localhost:{WEB_PORT}"


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
    assert _port_free(API_PORT) and _port_free(WEB_PORT), "e2e ports must be free"
    env = dict(os.environ)
    env["CORS_ORIGINS"] = WEB
    env.setdefault("JWT_SECRET_KEY", "test-only-secret")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(API_PORT)],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    npm = "npm.cmd" if os.name == "nt" else "npm"
    web = subprocess.Popen(
        [npm, "run", "dev", "--", "--port", str(WEB_PORT), "--strictPort"],
        cwd=ROOT / "frontend", env=dict(env, VITE_API_URL=API), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
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


# ---- rounds UI and the application's current round (user-approved requirement) ----

@pytest.fixture(scope="module")
def round_app(servers, creds, company):
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
    a = call("POST", "/applications", {"company_id": company["id"], "notes": "rounds app"}, tok)
    return {"app": a, "token": tok, "call": call}


def test_12_create_round(browser, creds, round_app):
    d = browser
    login(d, creds)
    wait(d, lambda x: len(rows(x)) >= 1)
    rows(d)[0].find_element(By.LINK_TEXT, "Rounds").click()
    wait(d, lambda x: x.current_url.endswith("/rounds"))
    text_present(d, "This application has no rounds yet")
    d.find_element(By.XPATH, "//button[text()='+ New round']").click()
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    assert alert_text(d) == "Round name is required"
    d.find_element(By.XPATH, "//label[contains(.,'Round name')]//input").send_keys(PREFIX + "Tech1")
    d.find_element(By.TAG_NAME, "textarea").send_keys("went well")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: len(rows(x)) == 1)
    assert PREFIX + "Tech1" in rows(d)[0].text and "PENDING" in rows(d)[0].text
    assert "went well" in rows(d)[0].text


def test_13_edit_round(browser):
    d = browser
    rows(d)[0].find_element(By.XPATH, ".//button[text()='Edit']").click()
    name = d.find_element(By.XPATH, "//label[contains(.,'Round name')]//input")
    wait(d, lambda x: name.get_attribute("value") == PREFIX + "Tech1")
    name.clear()
    name.send_keys(PREFIX + "Tech1b")
    Select(d.find_element(By.XPATH, "//form//select")).select_by_value("PASSED")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: len(rows(x)) == 1 and PREFIX + "Tech1b" in rows(x)[0].text)
    assert "PASSED" in rows(d)[0].text


def test_14_set_and_clear_current_round(browser, round_app):
    d = browser
    aid = round_app["app"]["id"]
    d.get(WEB + f"/applications/{aid}/edit")
    sel_loc = (By.XPATH, "//label[contains(.,'Current round')]//select")
    wait(d, lambda x: len(Select(x.find_element(*sel_loc)).options) == 2)
    Select(d.find_element(*sel_loc)).select_by_visible_text(PREFIX + "Tech1b")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: path(x) == "/applications")
    got = round_app["call"]("GET", f"/applications/{aid}", token=round_app["token"])
    assert got["round_id"] is not None
    # rounds page marks it as current
    d.get(WEB + f"/applications/{aid}/rounds")
    wait(d, lambda x: "(current)" in x.find_element(By.TAG_NAME, "body").text)
    # clear it again
    d.get(WEB + f"/applications/{aid}/edit")
    wait(d, lambda x: Select(x.find_element(*sel_loc)).first_selected_option.text == PREFIX + "Tech1b")
    Select(d.find_element(*sel_loc)).select_by_value("")
    d.find_element(By.XPATH, "//button[text()='Save']").click()
    wait(d, lambda x: path(x) == "/applications")
    assert round_app["call"]("GET", f"/applications/{aid}", token=round_app["token"])["round_id"] is None


def test_15_delete_round_clears_current_round(browser, round_app):
    d = browser
    aid = round_app["app"]["id"]
    rid = round_app["call"]("GET", f"/applications/{aid}/rounds", token=round_app["token"])[0]["id"]
    round_app["call"]("PUT", f"/applications/{aid}", {"round_id": rid}, round_app["token"])
    d.get(WEB + f"/applications/{aid}/rounds")
    wait(d, lambda x: len(rows(x)) == 1)
    rows(d)[0].find_element(By.XPATH, ".//button[text()='Delete']").click()
    dialog = wait(d, EC.visibility_of_element_located((By.CSS_SELECTOR, "[role=dialog]")))
    dialog.find_element(By.XPATH, ".//button[text()='Cancel']").click()
    wait(d, EC.invisibility_of_element_located((By.CSS_SELECTOR, "[role=dialog]")))
    assert len(rows(d)) == 1
    rows(d)[0].find_element(By.XPATH, ".//button[text()='Delete']").click()
    d.find_element(By.CSS_SELECTOR, "[role=dialog]").find_element(By.XPATH, ".//button[text()='Delete']").click()
    text_present(d, "This application has no rounds yet")
    assert round_app["call"]("GET", f"/applications/{aid}", token=round_app["token"])["round_id"] is None
