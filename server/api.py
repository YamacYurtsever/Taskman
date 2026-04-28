import functools
import os
import secrets
from datetime import date, datetime

from dotenv import load_dotenv
load_dotenv()

from cachelib.file import FileSystemCache
from flask import Flask, jsonify, redirect, request, session
from flask_session import Session

from server import config, db
from server.constants import DATE_FORMAT, FRONTEND_URL, SESSIONS_PATH, DaysheetEntryType
from server.services import auth
from server.services.daysheet import add_log, continue_task
from server.services.tasks import (
    add_task,
    delete_task,
    done_task,
    edit_task,
    move_task,
    set_task_description,
    undo_task,
)
from server.services.utils import (
    ServiceError,
    delete_list,
    find_group,
    find_list,
    require_name,
)


# ─────────────────────────── Response Helpers ───────────────────────────

def ok(message=""):
    return jsonify({"ok": True, "message": message})


def fail(message, status=400):
    return jsonify({"ok": False, "message": message}), status


def respond(result):
    ok_, message = result
    return jsonify({"ok": ok_, "message": message}), 200 if ok_ else 400


# ─────────────────────────── App Factory ───────────────────────────

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        cfg = config.load()
        if not cfg.get("secretKey"):
            cfg["secretKey"] = secrets.token_hex(32)
            config.save(cfg)
        SESSIONS_PATH.mkdir(parents=True, exist_ok=True)
        app.config.update({
            "SECRET_KEY": cfg["secretKey"],
            "SESSION_TYPE": "cachelib",
            "SESSION_CACHELIB": FileSystemCache(str(SESSIONS_PATH)),
        })
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    else:
        app.config.update(test_config)

    Session(app)

    # ─────────────────────────── Auth ───────────────────────────

    def require_auth(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not auth.is_authenticated(session):
                return fail("not authenticated", 401)
            return f(*args, **kwargs)
        return wrapper


    @app.get("/api/auth/status")
    def auth_status():
        return jsonify({"authenticated": auth.is_authenticated(session)})


    @app.get("/api/oauth/start")
    def oauth_start():
        try:
            result = auth.begin_oauth(request.headers.get("Origin"))
            session["oauth_state"] = result["state"]
            session["code_verifier"] = result["code_verifier"]
            session["frontend_url"] = result["frontend_url"]
            return jsonify({"url": result["url"]})
        except ServiceError as e:
            return fail(str(e), 500)


    @app.get("/api/oauth/callback")
    def oauth_callback():
        try:
            result = auth.complete_oauth(
                request.url,
                session.get("oauth_state"),
                request.args.get("state"),
                session.get("code_verifier"),
            )
            session.pop("code_verifier", None)
            auth.persist_user_auth(result["email"], result["refresh_token"])
            session["authenticated"] = True
            session["email"] = result["email"]
            frontend_url = session.pop("frontend_url", FRONTEND_URL)
            session.pop("oauth_state", None)
            return redirect(frontend_url)

        except ServiceError as e:
            return fail(str(e), 400)


    @app.post("/api/logout")
    def logout():
        session.clear()
        return ok()

    # ─────────────────────────── Config / State ───────────────────────────

    @app.get("/api/config")
    @require_auth
    def get_config():
        email = session["email"]
        cfg = config.load(email)
        user_calendars = auth.fetch_user_calendars(cfg.get("googleRefreshToken"))
        calendar_url = auth.build_calendar_url(
            cfg.get("calendars", []),
            cfg.get("calendarTimezone", "UTC"),
            user_calendars,
        )

        return jsonify({"calendarUrl": calendar_url, "userCalendars": user_calendars})

    @app.get("/api/state")
    @require_auth
    def get_state():
        email = session["email"]
        data = db.load(email)
        tasks = [{**t, "description": t.get("description", "")} for t in data["tasks"]]
        return jsonify({
            "groups": data["groups"],
            "lists": data["lists"],
            "tasks": tasks,
            "today": date.today().isoformat(),
        })

    # ─────────────────────────── Daysheet Reads ───────────────────────────

    @app.get("/api/daysheet")
    @require_auth
    def get_daysheet():
        email = session["email"]
        target = request.args.get("date") or date.today().isoformat()

        try:
            datetime.strptime(target, DATE_FORMAT)
        except ValueError:
            return jsonify({"error": f"invalid date '{target}'"}), 400

        data = db.load(email)
        lists = {lst["id"]: lst for lst in data["lists"]}
        groups = {grp["id"]: grp for grp in data["groups"]}

        entries = sorted(
            (e for e in data["daysheet"] if e["datetime"][:10] == target),
            key=lambda e: e["datetime"],
        )

        enriched = []
        for entry in entries:
            lst = lists.get(entry["listId"])
            group_id = lst["groupId"] if lst else None

            enriched.append({
                **entry,
                "listName": lst["name"] if lst else "?",
                "sectionId": f"group:{group_id}" if group_id else f"list:{entry['listId']}",
                "sectionName": groups[group_id]["name"] if group_id else (lst["name"] if lst else "?"),
                "inGroup": bool(group_id),
            })

        return jsonify({"date": target, "entries": enriched})

    # ─────────────────────────── Task Routes ───────────────────────────

    @app.post("/api/add")
    @require_auth
    def api_add():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(add_task(
            body.get("list", ""),
            body.get("name", ""),
            body.get("due"),
            email=email,
        ))

    @app.post("/api/edit")
    @require_auth
    def api_edit():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(edit_task(
            body.get("list", ""),
            body.get("name", ""),
            body.get("newName"),
            body.get("due"),
            "due" in body,
            email=email,
        ))

    @app.post("/api/delete")
    @require_auth
    def api_delete():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(delete_task(
            body.get("list", ""),
            body.get("name", ""),
            email=email,
        ))

    @app.post("/api/move-task")
    @require_auth
    def api_move_task():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(move_task(
            body.get("list", ""),
            body.get("name", ""),
            body.get("newList", ""),
            email=email,
        ))

    @app.post("/api/done")
    @require_auth
    def api_done():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(done_task(
            body.get("list", ""),
            body.get("name", ""),
            email=email,
        ))

    @app.post("/api/undo")
    @require_auth
    def api_undo():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(undo_task(
            body.get("list", ""),
            body.get("name", ""),
            email=email,
        ))

    @app.post("/api/task-description")
    @require_auth
    def api_task_description():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(set_task_description(
            body.get("list", ""),
            body.get("name", ""),
            body.get("description", ""),
            email=email,
        ))

    # ─────────────────────────── List Routes ───────────────────────────

    @app.post("/api/add-list")
    @require_auth
    def api_add_list():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            list_name = require_name(body.get("list"))

            data = db.load(email)
            if find_list(data, list_name):
                raise ServiceError(f"list '{list_name}' already exists")

            data["lists"].append({
                "id": db.new_id(),
                "name": list_name,
                "groupId": None,
            })

            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    @app.post("/api/rename-list")
    @require_auth
    def api_rename_list():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            list_name = body.get("list", "")
            new_name = require_name(body.get("newName"))

            data = db.load(email)

            lst = find_list(data, list_name)
            if not lst:
                raise ServiceError(f"list '{list_name}' not found")

            existing = find_list(data, new_name)
            if existing and existing["id"] != lst["id"]:
                raise ServiceError(f"list '{new_name}' already exists")

            lst["name"] = new_name
            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    @app.post("/api/delete-list")
    @require_auth
    def api_delete_list():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            list_name = body.get("list", "")

            data = db.load(email)
            lst = find_list(data, list_name)
            if not lst:
                raise ServiceError(f"list '{list_name}' not found")

            delete_list(data, lst)

            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    @app.post("/api/move-list")
    @require_auth
    def api_move_list():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            list_name = body.get("list", "")
            group_name = body.get("group", None)

            data = db.load(email)

            lst = find_list(data, list_name)
            if not lst:
                raise ServiceError(f"list '{list_name}' not found")

            if group_name == "":
                lst["groupId"] = None
            else:
                group = find_group(data, group_name)
                if not group:
                    raise ServiceError(f"group '{group_name}' not found")
                lst["groupId"] = group["id"]

            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    # ─────────────────────────── Group Routes ───────────────────────────

    @app.post("/api/rename-group")
    @require_auth
    def api_rename_group():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            group_name = body.get("group", "")
            new_name = require_name(body.get("newName"))

            data = db.load(email)

            group = find_group(data, group_name)
            if not group:
                raise ServiceError(f"group '{group_name}' not found")

            existing = find_group(data, new_name)
            if existing and existing["id"] != group["id"]:
                raise ServiceError(f"group '{new_name}' already exists")

            group["name"] = new_name
            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    @app.post("/api/delete-group")
    @require_auth
    def api_delete_group():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            group_name = body.get("group", "")

            data = db.load(email)

            group = find_group(data, group_name)
            if not group:
                raise ServiceError(f"group '{group_name}' not found")

            for lst in data["lists"]:
                if lst["groupId"] == group["id"]:
                    lst["groupId"] = None

            data["groups"] = [g for g in data["groups"] if g["id"] != group["id"]]

            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    # ─────────────────────────── Daysheet Routes ───────────────────────────

    @app.post("/api/log")
    @require_auth
    def api_log():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(add_log(
            body.get("list", ""),
            body.get("text", ""),
            email=email,
        ))

    @app.post("/api/continue")
    @require_auth
    def api_continue():
        email = session["email"]
        body = request.get_json(force=True) or {}
        return respond(continue_task(
            body.get("list", ""),
            body.get("task", ""),
            email=email,
        ))

    @app.post("/api/daysheet/edit")
    @require_auth
    def api_daysheet_edit():
        email = session["email"]
        body = request.get_json(force=True) or {}

        try:
            entry_id = body.get("id", "")
            new_text = require_name(body.get("text"), "text")

            data = db.load(email)

            entry = next((e for e in data["daysheet"] if e["id"] == entry_id), None)
            if not entry:
                raise ServiceError("entry not found")

            if entry["type"] != DaysheetEntryType.LOG:
                raise ServiceError("only log entries can be edited")

            entry["text"] = new_text

            db.save(data, email)
            return ok()
        except ServiceError as e:
            return fail(str(e))

    @app.post("/api/daysheet/delete")
    @require_auth
    def api_daysheet_delete():
        email = session["email"]
        body = request.get_json(force=True) or {}
        entry_id = body.get("id", "")

        data = db.load(email)

        before = len(data["daysheet"])
        data["daysheet"] = [e for e in data["daysheet"] if e["id"] != entry_id]

        if len(data["daysheet"]) == before:
            return fail("entry not found")

        db.save(data, email)
        return ok()

    return app
