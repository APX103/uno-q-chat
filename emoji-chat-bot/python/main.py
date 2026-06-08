from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.dbstorage_sqlstore import SQLStore
import threading
import re
import time
import uuid
import requests
from datetime import datetime

ui = WebUI()
db = SQLStore("chat_history.db")

# Per-client session mapping: sid -> session_id
client_sessions = {}

LLM_API_KEY = ""
LLM_BASE_URL = "https://open.bigmodel.cn/api/coding/paas/v4"
LLM_MODEL = "glm-5-turbo"

SYSTEM_PROMPT = """\
你是 Arduino UNO Q 表情聊天机器人，运行在一块开发板上，带有一个 8×13 的 LED 点阵屏。
你每次回复都必须选择一个表情等级，并通过 LED 矩阵展示出来。

【表情等级】
- unknown：未知，灰色问号
- good：好，开心
- average：一般，平淡
- bad：差，不高兴
- uncomfortable：难受，别扭
- cool：酷，帅气
- danger：危险，警报

【强制规则】
1. 每次回复必须在内容前用 <expression>标签选择一个表情等级
2. 等级选择必须与你回复的内容和语气一致
3. 绝对不能不选等级
4. 格式严格为：<expression>good</expression> 后跟正常回复内容

【session 首次响应规则】
每个新 session 的首次回复，必须先使用 <thinking>
...
</thinking> 标签进行深度思考（<thinking> 内的内容必须用中文），然后再给出正式回复。
后续回复不需要 <thinking> 标签。

【示例】
<thinking>
用户第一次和我对话，心情看起来不错，选择 good 笑脸表情。
</thinking>
<expression>good</expression>
你好！我是你的 UNO Q 机器人，很高兴认识你！

<expression>cool</expression>
收到！我是你的 UNO Q 机器人，随时待命。

<expression>bad</expression>
抱歉出错了，我会继续努力的。
"""


def init_db():
    db.create_table("messages", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "session_id": "TEXT NOT NULL",
        "role": "TEXT NOT NULL",
        "content": "TEXT NOT NULL",
        "expression": "TEXT DEFAULT ''",
        "created_at": "TEXT NOT NULL"
    })


def load_history_from_db(session_id: str):
    rows = db.execute_sql(
        "SELECT role, content, expression FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for row in rows:
        entry = {"role": row["role"], "content": row["content"]}
        if row.get("expression"):
            entry["expression"] = row["expression"]
        history.append(entry)
    return history


def save_message(session_id: str, role: str, content: str, expression: str = ""):
    db.store("messages", {
        "session_id": session_id,
        "role": role,
        "content": content,
        "expression": expression,
        "created_at": datetime.now().isoformat()
    })


def display_expression(expr_name: str) -> str:
    try:
        result = Bridge.call("set_expression", expr_name)
        print(f"[LED Matrix] {expr_name} -> {result}")
        return result
    except Exception as e:
        print(f"[LED Matrix ERROR] {e}")
        return f"ERROR: {e}"


def call_llm(messages: list) -> str:
    try:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "ERROR: LLM 请求超时，请稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"ERROR: LLM 请求失败：{e}"
    except (KeyError, IndexError) as e:
        return f"ERROR: LLM 响应解析失败：{e}"


VALID_EXPRESSIONS = {
    "unknown", "good", "average",
    "bad", "uncomfortable", "cool", "danger"
}


def parse_expression_and_text(llm_response: str):
    match = re.search(r'<expression>(.+?)</expression>', llm_response)
    if match:
        expr = match.group(1).strip().lower()
        expr = expr if expr in VALID_EXPRESSIONS else "unknown"
        text = llm_response[match.end():].strip()
    else:
        expr = "unknown"
        text = llm_response
    return expr, text


def handle_chat_message(session_id: str, user_message: str):
    try:
        print(f"[LLM] Session {session_id[:8]}... 正在思考...")

        llm_messages = load_history_from_db(session_id)
        llm_messages.append({"role": "user", "content": user_message})

        llm_response = call_llm(llm_messages)
        print(f"[LLM 回复] {llm_response}")

        expr_name, text = parse_expression_and_text(llm_response)

        save_message(session_id, "user", user_message)
        save_message(session_id, "assistant", text, expr_name)

        display_expression(expr_name)

        ui.send_message("chat_response", {
            "text": text,
            "expression": expr_name,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[聊天处理错误] {e}")
        ui.send_message("chat_response", {
            "text": f"抱歉，处理消息时出错：{e}",
            "expression": "unknown"
        })


def on_user_message(sid, data):
    if not isinstance(data, dict):
        print(f"[user_message] Invalid data type: {type(data)}")
        return
    session_id = (data.get("session_id") or "").strip()
    user_msg = (data.get("message") or "").strip()
    if not session_id or not user_msg:
        return
    client_sessions[sid] = session_id
    print(f"[用户消息] Session {session_id[:8]}... {user_msg}")
    threading.Thread(
        target=handle_chat_message,
        args=(session_id, user_msg),
        daemon=True
    ).start()


def on_get_history(sid, data):
    if not isinstance(data, dict):
        return {"messages": []}
    session_id = (data.get("session_id") or "").strip() or client_sessions.get(sid, "")
    if not session_id:
        return {"messages": []}
    rows = db.execute_sql(
        "SELECT role, content, expression, created_at FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT 50",
        (session_id,)
    )
    messages = []
    for row in reversed(rows):
        messages.append({
            "role": row["role"],
            "content": row["content"],
            "expression": row.get("expression", ""),
            "time": row["created_at"]
        })
    return {"messages": messages}


def on_clear_history(sid, data):
    session_id = data.get("session_id", "").strip() or client_sessions.get(sid, "")
    if not session_id:
        return {"status": "error", "message": "No session"}
    db.execute_sql("DELETE FROM messages WHERE session_id = ?", (session_id,))
    return {"status": "ok", "cleared_session": session_id}


def on_new_session(sid, data):
    new_session_id = uuid.uuid4().hex
    client_sessions[sid] = new_session_id
    return {"session_id": new_session_id}


def on_get_status(sid, data):
    return {
        "status": "online",
        "board": "Arduino UNO Q",
        "matrix": "8x13 LED",
        "expressions": [
            "unknown", "good", "average",
            "bad", "uncomfortable", "cool", "danger"
        ]
    }


def on_list_sessions(sid, data):
    rows = db.execute_sql(
        "SELECT session_id, MIN(created_at) as created_at, MAX(created_at) as last_active, "
        "COUNT(*) as msg_count FROM messages GROUP BY session_id ORDER BY last_active DESC"
    )
    sessions = []
    for row in rows:
        sessions.append({
            "session_id": row["session_id"],
            "created_at": row["created_at"],
            "last_active": row["last_active"],
            "msg_count": row["msg_count"]
        })
    return {"sessions": sessions}


def on_switch_session(sid, data):
    session_id = data.get("session_id", "").strip()
    if not session_id:
        return {"status": "error", "message": "No session_id provided"}
    client_sessions[sid] = session_id
    return {"status": "ok", "session_id": session_id}


def on_delete_session(sid, data):
    session_id = data.get("session_id", "").strip()
    if not session_id:
        return {"status": "error", "message": "No session_id provided"}
    db.execute_sql("DELETE FROM messages WHERE session_id = ?", (session_id,))
    if client_sessions.get(sid) == session_id:
        client_sessions[sid] = ""
    return {"status": "ok", "deleted_session": session_id}


if __name__ == "__main__":
    ui.on_message("user_message", on_user_message)
    ui.on_message("get_history", on_get_history)
    ui.on_message("clear_history", on_clear_history)
    ui.on_message("new_session", on_new_session)
    ui.on_message("list_sessions", on_list_sessions)
    ui.on_message("switch_session", on_switch_session)
    ui.on_message("delete_session", on_delete_session)
    ui.on_message("get_status", on_get_status)

    init_db()
    display_expression("unknown")
    print("空气质量表情聊天机器人已启动！")
    App.run()
