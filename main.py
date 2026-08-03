import asyncio
import json
import time
import urllib.request
import urllib.error
import flet as ft

try:
    import flet_video as ftv
except ImportError:
    ftv = None

try:
    import flet_webview as ftwv
except ImportError:
    ftwv = None

# =============================================
# SUPABASE - قاعدة بيانات مشتركة بين كل المستخدمين
# (تستخدم urllib فقط، بدون أي مكتبات خارجية إضافية،
#  حتى لا تحتاج لتثبيت أي حزمة جديدة)
# =============================================
SUPABASE_URL = "https://hdtrnfpwyvaeziaiweck.supabase.co"
SUPABASE_KEY = "sb_publishable_XYiUfizde8-Z0yBjvZNsBw_q_LSXK7V"
SUPABASE_TABLE = "app_content"
SUPABASE_ROW_ID = "main"


def _supabase_request(method, path, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else None


def _supabase_get_contents_sync():
    result = _supabase_request(
        "GET", f"{SUPABASE_TABLE}?id=eq.{SUPABASE_ROW_ID}&select=contents"
    )
    if result and len(result) > 0:
        return result[0].get("contents")
    return None


def _supabase_save_contents_sync(contents):
    _supabase_request(
        "POST",
        SUPABASE_TABLE,
        {"id": SUPABASE_ROW_ID, "contents": contents},
    )


async def supabase_get_contents():
    try:
        return await asyncio.to_thread(_supabase_get_contents_sync)
    except Exception as ex:
        print("Supabase load error:", ex)
        return None


async def supabase_save_contents(contents):
    try:
        await asyncio.to_thread(_supabase_save_contents_sync, contents)
        return True
    except Exception as ex:
        print("Supabase save error:", ex)
        return False


def _safe_enum(class_name, value_name, fallback_str):
    """يرجع قيمة enum من مكتبة Flet إن وجدت، وإلا نص بديل مكافئ
    (Flet يقبل نصوص بدل الـ enum في أغلب الإصدارات)."""
    cls = getattr(ft, class_name, None)
    if cls is not None:
        val = getattr(cls, value_name, None)
        if val is not None:
            return val
    return fallback_str


# =============================================
# فتح/إغلاق الحوارات بشكل متوافق مع كل إصدارات Flet
# (بعض الإصدارات القديمة أو غير القياسية لا تحتوي
#  على page.open / page.close)
# =============================================
def _open_dialog(page, dlg):
    if hasattr(page, "open"):
        try:
            page.open(dlg)
            return
        except Exception:
            pass
    if hasattr(page, "show_dialog_async") and hasattr(page, "run_task"):
        try:
            page.run_task(page.show_dialog_async, dlg)
            return
        except Exception:
            pass
    try:
        if hasattr(page, "overlay") and dlg not in page.overlay:
            page.overlay.append(dlg)
    except Exception:
        pass
    try:
        dlg.open = True
    except Exception:
        pass
    try:
        page.dialog = dlg
    except Exception:
        pass
    page.update()


def _close_dialog(page, dlg):
    if hasattr(page, "close"):
        try:
            page.close(dlg)
            return
        except Exception:
            pass
    if hasattr(page, "close_dialog_async") and hasattr(page, "run_task"):
        try:
            page.run_task(page.close_dialog_async)
            return
        except Exception:
            pass
    try:
        dlg.open = False
    except Exception:
        pass
    page.update()


# =============================================
# محاذاة متوافقة مع كل إصدارات Flet
# (بعض الإصدارات لا تحتوي على ALIGN_CENTER مباشرة)
# =============================================
def _safe_alignment(name, x, y):
    try:
        val = getattr(ft.alignment, name, None)
        if val is not None:
            return val
    except Exception:
        pass
    try:
        return ft.alignment.Alignment(x, y)
    except Exception:
        return None


ALIGN_CENTER = _safe_alignment("center", 0, 0)
ALIGN_TOP_LEFT = _safe_alignment("top_left", -1, -1)
ALIGN_BOTTOM_RIGHT = _safe_alignment("bottom_right", 1, 1)

# =============================================
# بيانات الدخول (كما في التطبيق الأصلي)
# =============================================
CREDS = {"email": "admin@difa.com", "password": "admin123"}

# =============================================
# الألوان (نفس متغيرات CSS في الأصل)
# =============================================
COLORS_LIGHT = {
    "bg": "#f0f2f7",
    "bg_card": "#ffffff",
    "bg_header": "#ffffff",
    "text": "#1a2332",
    "text_secondary": "#6a7a8a",
    "primary": "#2d7fc1",
    "primary_dark": "#1a5a8a",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "success": "#27ae60",
    "border": "#e0e5ec",
    "bottom_nav": "#ffffff",
}

COLORS_DARK = {
    "bg": "#0f1724",
    "bg_card": "#1a2639",
    "bg_header": "#0f1724",
    "text": "#e8edf2",
    "text_secondary": "#8899aa",
    "primary": "#2d7fc1",
    "primary_dark": "#1a5a8a",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "success": "#27ae60",
    "border": "#2a3a4a",
    "bottom_nav": "#1a2639",
}


async def main(page: ft.Page):
    page.title = "ديف كرتون"
    page.rtl = True
    page.padding = 0
    page.bgcolor = COLORS_LIGHT["bg"]
    page.fonts = {
        "Tajawal": "https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap"
    }
    page.theme = ft.Theme(font_family="Tajawal")
    page.dark_theme = ft.Theme(font_family="Tajawal")
    page.window.width = 480
    page.window.height = 860

    # =============================================
    # STATE - الحالة العامة للتطبيق
    # =============================================
    state = {
        "contents": [],          # قائمة الأعمال (أنمي/كرتون)
        "is_dark": False,        # الوضع الليلي
        "is_published": False,   # حالة النشر
        "last_publish": "",      # وقت آخر نشر
        "current_section": "home",   # القسم الحالي (home/anime/cartoon)
        "search_query": "",
        "admin_open": False,     # هل لوحة الإدارة مفتوحة
        "admin_click_count": 0,
        "admin_last_click": 0.0,
        "login_attempts": 0,
        "admin_tab": "add",      # إضافة / إدارة / إعدادات
        "selected_season_index": 0,
        "current_content_id": None,
    }

    # =============================================
    # PERSISTENCE - قاعدة بيانات محلية (بديل localStorage)
    # يدعم إصدارات Flet المختلفة (client_storage قد لا تكون
    # متوفرة في كل إصدار)، ويستخدم تخزين في الذاكرة كبديل آمن
    # بحيث لا يتوقف التطبيق عن العمل أبداً.
    # =============================================
    _memory_store = {}

    async def _storage_get(key):
        cs = getattr(page, "client_storage", None)
        if cs is not None:
            try:
                if hasattr(cs, "get_async"):
                    return await cs.get_async(key)
                if hasattr(cs, "get"):
                    return cs.get(key)
            except Exception:
                pass
        return _memory_store.get(key)

    async def _storage_set(key, value):
        cs = getattr(page, "client_storage", None)
        if cs is not None:
            try:
                if hasattr(cs, "set_async"):
                    await cs.set_async(key, value)
                    return
                if hasattr(cs, "set"):
                    cs.set(key, value)
                    return
            except Exception:
                pass
        _memory_store[key] = value

    async def save_data():
        await _storage_set("contents", json.dumps(state["contents"]))
        await supabase_save_contents(state["contents"])

    async def load_data():
        remote = await supabase_get_contents()
        if isinstance(remote, list):
            state["contents"] = remote
            await _storage_set("contents", json.dumps(state["contents"]))
            return
        try:
            raw = await _storage_get("contents")
            if raw:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    state["contents"] = parsed
                    return
        except Exception:
            pass
        state["contents"] = []
        await save_data()

    async def load_theme():
        theme = await _storage_get("theme")
        state["is_dark"] = theme == "dark"

    async def save_theme():
        await _storage_set("theme", "dark" if state["is_dark"] else "light")

    async def load_publish_status():
        pub = await _storage_get("isPublished")
        state["is_published"] = pub == "true"
        last = await _storage_get("lastPublish")
        state["last_publish"] = last or "اليوم"

    async def save_publish_status():
        await _storage_set("isPublished", "true" if state["is_published"] else "false")
        if state["is_published"]:
            await _storage_set("lastPublish", time.strftime("%Y-%m-%d %H:%M"))

    # =============================================
    # HELPERS
    # =============================================
    def c(key):
        return (COLORS_DARK if state["is_dark"] else COLORS_LIGHT)[key]

    def show_toast(msg: str, kind: str = "success"):
        color = c("success") if kind == "success" else (c("danger") if kind == "error" else c("primary"))
        _open_dialog(page, 
            ft.SnackBar(
                content=ft.Text(msg, color=ft.Colors.WHITE),
                bgcolor=color,
                duration=2500,
            )
        )

    def next_id():
        return int(time.time() * 1000)

    def find_content(cid):
        for item in state["contents"]:
            if item["id"] == cid:
                return item
        return None

    def confirm_dialog(title: str, message: str, on_yes):
        async def yes_click(e):
            _close_dialog(page, dlg)
            await on_yes()

        def no_click(e):
            _close_dialog(page, dlg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("إلغاء", on_click=no_click),
                ft.ElevatedButton(
                    "تأكيد", bgcolor=c("danger"), color=ft.Colors.WHITE, on_click=yes_click
                ),
            ],
        )
        _open_dialog(page, dlg)

    # =============================================
    # UI ROOT CONTAINERS
    # =============================================
    root = ft.Column(spacing=0, expand=True)
    page.add(root)

    # ============================================================
    # HEADER
    # ============================================================
    async def on_title_click(e):
        now = time.time()
        if now - state["admin_last_click"] > 2:
            state["admin_click_count"] = 0
        state["admin_last_click"] = now
        state["admin_click_count"] += 1
        if state["admin_click_count"] >= 3:
            state["admin_click_count"] = 0
            if state["admin_open"]:
                state["admin_open"] = False
                show_toast("تم إغلاق لوحة الإدارة")
                render()
            else:
                open_login_dialog()

    async def on_theme_toggle(e):
        state["is_dark"] = not state["is_dark"]
        await save_theme()
        page.bgcolor = c("bg")
        show_toast("تم تفعيل الوضع الليلي" if state["is_dark"] else "تم تفعيل الوضع النهاري")
        render()

    def build_header():
        return ft.Container(
            bgcolor=c("bg_header"),
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(3, c("primary"))),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.MOVIE, color=c("primary"), size=26),
                            ft.Container(
                                content=ft.Text(
                                    "ديف كرتون",
                                    size=19,
                                    weight=ft.FontWeight.W_800,
                                    color=c("primary"),
                                ),
                                on_click=on_title_click,
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=6,
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DARK_MODE if not state["is_dark"] else ft.Icons.LIGHT_MODE,
                        icon_color=c("text"),
                        bgcolor=c("bg"),
                        on_click=on_theme_toggle,
                        style=ft.ButtonStyle(shape=ft.CircleBorder()),
                    ),
                ],
            ),
        )

    # ============================================================
    # SEARCH BAR
    # ============================================================
    def on_search_change(e):
        state["search_query"] = e.control.value.strip().lower()
        render()

    def build_search_bar():
        return ft.Container(
            bgcolor=c("bg_card"),
            border_radius=50,
            border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
            padding=ft.Padding(left=14, right=4, top=4, bottom=4),
            margin=ft.Margin(left=0, right=0, top=0, bottom=14),
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE, size=18),
                        bgcolor=c("primary"),
                        border_radius=50,
                        padding=8,
                    ),
                    ft.TextField(
                        value=state["search_query"],
                        hint_text="ابحث عن عمل...",
                        border=ft.InputBorder.NONE,
                        text_size=14,
                        color=c("text"),
                        expand=True,
                        on_change=on_search_change,
                    ),
                ],
                spacing=8,
            ),
        )

    # ============================================================
    # CONTENT CARDS
    # ============================================================
    def build_card(item):
        thumb_children = []
        if item.get("image"):
            thumb_children.append(
                ft.Image(
                    src=item["image"],
                    fit=_safe_enum("ImageFit", "COVER", "cover"),
                    width=150,
                    height=140,
                    error_content=ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE70, size=40),
                )
            )
        else:
            thumb_children.append(ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.WHITE70, size=40))

        badge_color = "#8e44ad" if item["type"] == "anime" else c("primary")
        badge_text = "أنمي" if item["type"] == "anime" else "كرتون"

        return ft.Container(
            width=150,
            bgcolor=c("bg_card"),
            border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
            border_radius=14,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda e, it=item: open_content_viewer(it),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        width=150,
                        height=140,
                        gradient=ft.LinearGradient(
                            begin=ALIGN_TOP_LEFT,
                            end=ALIGN_BOTTOM_RIGHT,
                            colors=["#1a3a5a", "#0f2030"],
                        ),
                        alignment=ALIGN_CENTER,
                        content=ft.Stack(controls=thumb_children),
                    ),
                    ft.Container(
                        padding=ft.Padding(left=10, right=10, top=6, bottom=8),
                        border=ft.Border(top=ft.BorderSide(1, c("border"))),
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    item["title"],
                                    size=12,
                                    weight=ft.FontWeight.W_700,
                                    color=c("text"),
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Container(
                                    bgcolor=badge_color,
                                    border_radius=4,
                                    padding=ft.Padding(left=8, right=8, top=1, bottom=1),
                                    content=ft.Text(badge_text, size=9, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def build_section(icon, title, items, empty_icon, empty_text):
        if not items:
            body = ft.Container(
                padding=40,
                alignment=ALIGN_CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(empty_icon, size=48, color=c("text_secondary")),
                        ft.Text(empty_text, color=c("text_secondary")),
                    ],
                ),
            )
        else:
            body = ft.Row(
                controls=[build_card(it) for it in items],
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            )
        return ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(icon, color=c("primary"), size=18),
                        ft.Text(title, size=15, weight=ft.FontWeight.W_700, color=c("text")),
                        ft.Text(f"({len(items)})", size=11, color=c("text_secondary")),
                    ],
                ),
                body,
            ],
        )

    # ============================================================
    # CONTENT VIEWER (مشاهد - عرض المواسم والحلقات)
    # ============================================================
    def open_content_viewer(item):
        state["current_content_id"] = item["id"]
        state["selected_season_index"] = 0
        show_content_viewer_dialog()

    def show_content_viewer_dialog():
        item = find_content(state["current_content_id"])
        if not item:
            return
        seasons = item.get("seasons") or []

        if not seasons:
            body = ft.Container(
                padding=40,
                alignment=ALIGN_CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.LAYERS, size=40, color=c("text_secondary")),
                        ft.Text("لا توجد مواسم", color=c("text_secondary")),
                    ],
                ),
            )
        else:
            sel = state["selected_season_index"]
            if sel >= len(seasons):
                sel = 0
                state["selected_season_index"] = 0

            def select_season(idx):
                state["selected_season_index"] = idx
                show_content_viewer_dialog()

            season_chips = ft.Row(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=[
                    ft.Container(
                        width=90,
                        border=ft.Border(left=ft.BorderSide(2, c("primary") if i == sel else c("border")), top=ft.BorderSide(2, c("primary") if i == sel else c("border")), right=ft.BorderSide(2, c("primary") if i == sel else c("border")), bottom=ft.BorderSide(2, c("primary") if i == sel else c("border"))),
                        bgcolor=c("primary") if i == sel else None,
                        border_radius=14,
                        padding=12,
                        alignment=ALIGN_CENTER,
                        on_click=lambda e, i=i: select_season(i),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                            controls=[
                                ft.Text(
                                    str(s["number"]),
                                    size=18,
                                    weight=ft.FontWeight.W_800,
                                    color=ft.Colors.WHITE if i == sel else c("text"),
                                ),
                                ft.Text(
                                    "موسم",
                                    size=10,
                                    color=ft.Colors.WHITE70 if i == sel else c("text_secondary"),
                                ),
                            ],
                        ),
                    )
                    for i, s in enumerate(seasons)
                ],
            )

            episodes = seasons[sel].get("episodes") or []
            if episodes:
                ep_rows = []
                for ep in episodes:
                    ep_rows.append(
                        ft.Container(
                            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                            bgcolor=c("bg"),
                            border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
                            border_radius=12,
                            on_click=lambda e, u=ep["url"]: play_click(e, u),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                ep.get("title") or f"حلقة {ep['number']}",
                                                size=13,
                                                weight=ft.FontWeight.W_600,
                                                color=c("text"),
                                            ),
                                            ft.Text(
                                                f"حلقة {ep['number']}",
                                                size=10,
                                                color=c("text_secondary"),
                                            ),
                                        ],
                                    ),
                                    ft.ElevatedButton(
                                        "تشغيل",
                                        icon=ft.Icons.PLAY_ARROW,
                                        bgcolor=c("primary"),
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, u=ep["url"]: play_click(e, u),
                                    ),
                                ],
                            ),
                        )
                    )
                ep_list = ft.Column(spacing=6, controls=ep_rows)
            else:
                ep_list = ft.Container(
                    padding=12,
                    alignment=ALIGN_CENTER,
                    content=ft.Text("لا توجد حلقات في هذا الموسم", color=c("text_secondary"), size=13),
                )

            body = ft.Column(spacing=10, controls=[season_chips, ep_list])

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"📺 {item['title']}", color=c("primary")),
            content=ft.Container(content=body, width=380),
            actions=[
                ft.ElevatedButton(
                    "إغلاق",
                    icon=ft.Icons.CLOSE,
                    bgcolor=c("danger"),
                    color=ft.Colors.WHITE,
                    on_click=lambda e: _close_dialog(page, dlg),
                )
            ],
        )
        _open_dialog(page, dlg)

    # ============================================================
    # PLAYER (تشغيل الحلقة) - مشغل فيديو داخل التطبيق بدون متصفح
    # ============================================================
    def is_youtube_url(url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def extract_youtube_id(url: str):
        import re
        patterns = [
            r"youtu\.be/([A-Za-z0-9_-]{6,})",
            r"youtube\.com/watch\?v=([A-Za-z0-9_-]{6,})",
            r"youtube\.com/embed/([A-Za-z0-9_-]{6,})",
            r"youtube\.com/shorts/([A-Za-z0-9_-]{6,})",
        ]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)
        return None

    async def resolve_stream_url(url: str):
        """يحاول استخراج رابط تشغيل مباشر (خصوصاً لروابط يوتيوب) عبر yt-dlp.
        يرجع (stream_url, None) عند النجاح، أو (None, رسالة الخطأ) عند الفشل."""
        if not is_youtube_url(url):
            return url, None  # رابط فيديو مباشر أصلاً (mp4/m3u8...)
        try:
            import yt_dlp
        except ImportError:
            return None, "NOT_INSTALLED"

        def _extract():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "format": "best[ext=mp4]/best",
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("url")

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _extract)
            if not result:
                return None, "لم يتم العثور على رابط تشغيل مباشر لهذا الفيديو."
            return result, None
        except Exception as ex:
            return None, str(ex)

    async def open_player(url: str):
        if not url:
            show_toast("لا يوجد رابط", "error")
            return

        loading_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("تشغيل الحلقة"),
            content=ft.Container(
                width=280,
                height=100,
                alignment=ALIGN_CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressRing(),
                        ft.Text("جاري تجهيز الفيديو...", size=12, color=c("text_secondary")),
                    ],
                ),
            ),
        )
        _open_dialog(page, loading_dlg)

        # روابط يوتيوب: تُعرض عبر المشغّل الرسمي المضمّن (embed) مباشرة،
        # بدون استخراج رابط تشغيل مباشر عبر yt-dlp — هذا يفادي فحوصات
        # يوتيوب لمكافحة السحب الآلي، ويناسب المحتوى المملوك للناشر نفسه.
        if is_youtube_url(url):
            _close_dialog(page, loading_dlg)
            video_id = extract_youtube_id(url)
            if not video_id:
                fallback_dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("تعذّر تشغيل الفيديو"),
                    content=ft.Container(
                        width=320,
                        content=ft.Text(
                            "تعذّر التعرف على معرف فيديو يوتيوب من هذا الرابط.",
                            size=12, color=c("text_secondary"), selectable=True,
                        ),
                    ),
                    actions=[ft.TextButton("إغلاق", on_click=lambda e: _close_dialog(page, fallback_dlg))],
                )
                _open_dialog(page, fallback_dlg)
                return

            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&playsinline=1"
            watch_url = f"https://www.youtube.com/watch?v={video_id}"

            def _open_in_browser(e):
                page.launch_url(watch_url)

            try:
                if ftwv is None:
                    raise RuntimeError("حزمة flet-webview غير مثبتة")
                player_body = ft.Container(
                    height=260,
                    content=ftwv.WebView(url=embed_url, expand=True),
                )
            except Exception as ex:
                player_body = ft.Container(
                    height=140,
                    alignment=ALIGN_CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "تعذّر تشغيل مشغل يوتيوب الداخلي. تأكد من تثبيت:\n"
                                "python -m pip install flet-webview\n\n"
                                f"تفاصيل: {ex}",
                                size=12, color=c("text_secondary"), selectable=True,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                "فتح الفيديو بالمتصفح",
                                icon=ft.Icons.OPEN_IN_NEW,
                                on_click=_open_in_browser,
                            ),
                        ],
                    ),
                )

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("تشغيل الحلقة"),
                content=ft.Container(content=player_body, width=380),
                actions=[ft.TextButton("إغلاق", on_click=lambda e: _close_dialog(page, dlg))],
            )
            _open_dialog(page, dlg)
            return

        stream_url, error = await resolve_stream_url(url)

        _close_dialog(page, loading_dlg)

        if not stream_url:
            if error == "NOT_INSTALLED":
                msg = (
                    "لتشغيل روابط يوتيوب داخل التطبيق يجب تثبيت مكتبة yt-dlp "
                    "لنفس نسخة بايثون التي تشغّل بها التطبيق، مثال:\n\n"
                    "python -m pip install yt-dlp\n\n"
                    "بعد التثبيت أعد تشغيل التطبيق."
                )
            else:
                msg = (
                    "تعذّر استخراج رابط التشغيل من هذا الفيديو.\n"
                    "جرّب تحديث المكتبة بهذا الأمر ثم أعد المحاولة:\n\n"
                    "python -m pip install --upgrade yt-dlp\n\n"
                    f"تفاصيل الخطأ: {error}"
                )
            fallback_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("تعذّر تشغيل الفيديو"),
                content=ft.Container(
                    width=320,
                    content=ft.Text(msg, size=12, color=c("text_secondary"), selectable=True),
                ),
                actions=[ft.TextButton("إغلاق", on_click=lambda e: _close_dialog(page, fallback_dlg))],
            )
            _open_dialog(page, fallback_dlg)
            return


        try:
            if ftv is None:
                raise RuntimeError("حزمة flet-video غير مثبتة")
            video_player = ftv.Video(
                playlist=[ftv.VideoMedia(stream_url)],
                autoplay=True,
                fill_color=ft.Colors.BLACK,
                aspect_ratio=16 / 9,
                expand=True,
            )
            player_body = ft.Container(height=260, content=video_player)
        except Exception as ex:
            player_body = ft.Container(
                height=140,
                alignment=ALIGN_CENTER,
                content=ft.Text(
                    "تعذّر تشغيل مشغل الفيديو الداخلي. تأكد من تثبيت:\n"
                    "python -m pip install flet-video\n\n"
                    f"تفاصيل: {ex}",
                    size=12,
                    color=c("text_secondary"),
                    selectable=True,
                ),
            )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("تشغيل الحلقة"),
            content=ft.Container(content=player_body, width=380),
            actions=[ft.TextButton("إغلاق", on_click=lambda e: _close_dialog(page, dlg))],
        )
        _open_dialog(page, dlg)

    def play_click(e, u):
        page.run_task(open_player, u)

    # ============================================================
    # LOGIN DIALOG
    # ============================================================
    def open_login_dialog():
        email_field = ft.TextField(label="البريد الإلكتروني", autofocus=True)
        pass_field = ft.TextField(label="كلمة المرور", password=True, can_reveal_password=True)

        def do_login(e):
            email = (email_field.value or "").strip()
            pw = (pass_field.value or "").strip()
            if email == CREDS["email"] and pw == CREDS["password"]:
                _close_dialog(page, dlg)
                state["admin_open"] = True
                state["admin_tab"] = "add"
                show_toast("مرحباً في لوحة الإدارة")
                render()
            else:
                state["login_attempts"] += 1
                show_toast("البريد أو كلمة المرور غير صحيحة", "error")
                if state["login_attempts"] >= 3:
                    email_field.value = ""
                    pass_field.value = ""
                    state["login_attempts"] = 0
                    page.update()

        def cancel(e):
            _close_dialog(page, dlg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔒 تسجيل الدخول"),
            content=ft.Column(
                tight=True,
                width=300,
                controls=[
                    ft.Text("أدخل بيانات الدخول", color=c("text_secondary"), size=13),
                    email_field,
                    pass_field,
                ],
            ),
            actions=[
                ft.TextButton("إلغاء", on_click=cancel),
                ft.ElevatedButton(
                    "دخول", bgcolor=c("primary"), color=ft.Colors.WHITE, on_click=do_login
                ),
            ],
        )
        _open_dialog(page, dlg)

    # ============================================================
    # ADMIN: ADD CONTENT
    # ============================================================
    new_title_field = ft.TextField(label="اسم العمل")
    new_image_field = ft.TextField(label="رابط الصورة (غلاف العمل)")
    new_type_dropdown = ft.Dropdown(
        label="النوع",
        value="anime",
        options=[
            ft.dropdown.Option("anime", "أنمي"),
            ft.dropdown.Option("cartoon", "كرتون"),
        ],
    )

    async def add_content_click(e):
        title = (new_title_field.value or "").strip()
        image = (new_image_field.value or "").strip()
        content_type = new_type_dropdown.value or "anime"
        if not title:
            show_toast("⚠️ العنوان مطلوب", "error")
            return
        state["contents"].append(
            {"id": next_id(), "title": title, "image": image, "type": content_type, "seasons": []}
        )
        await save_data()
        new_title_field.value = ""
        new_image_field.value = ""
        show_toast("✅ تم الإضافة بنجاح")
        render()

    # ============================================================
    # ADMIN: MANAGE CONTENT LIST
    # ============================================================
    def build_manage_list():
        if not state["contents"]:
            return ft.Container(
                padding=30,
                alignment=ALIGN_CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY_2, size=40, color=c("text_secondary")),
                        ft.Text("لا يوجد محتوى", color=c("text_secondary")),
                    ],
                ),
            )
        rows = []
        for item in state["contents"]:
            rows.append(
                ft.Container(
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    bgcolor=c("bg"),
                    border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
                    border_radius=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(item["title"], size=13, weight=ft.FontWeight.W_600, color=c("text")),
                                    ft.Text(
                                        "أنمي" if item["type"] == "anime" else "كرتون",
                                        size=10,
                                        color=c("text_secondary"),
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.LAYERS,
                                        icon_color=ft.Colors.WHITE,
                                        bgcolor=c("primary"),
                                        icon_size=16,
                                        on_click=lambda e, it=item: open_admin_content_manager(it["id"]),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        icon_color=ft.Colors.WHITE,
                                        bgcolor=c("warning"),
                                        icon_size=16,
                                        on_click=lambda e, it=item: open_edit_content_dialog(it["id"]),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.WHITE,
                                        bgcolor=c("danger"),
                                        icon_size=16,
                                        on_click=lambda e, it=item: delete_content(it["id"]),
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )
        return ft.Column(spacing=6, controls=rows)

    def delete_content(cid):
        async def do_delete():
            state["contents"] = [c_ for c_ in state["contents"] if c_["id"] != cid]
            await save_data()
            show_toast("🗑️ تم الحذف", "error")
            render()

        confirm_dialog("حذف المحتوى", "حذف هذا المحتوى وجميع مواسمه وحلقاته؟", do_delete)

    def open_edit_content_dialog(cid):
        item = find_content(cid)
        if not item:
            return
        title_field = ft.TextField(label="العنوان الجديد", value=item["title"])
        image_field = ft.TextField(label="رابط الصورة الجديد", value=item.get("image") or "")

        async def save_click(e):
            new_title = (title_field.value or "").strip()
            if new_title:
                item["title"] = new_title
            item["image"] = (image_field.value or "").strip()
            await save_data()
            _close_dialog(page, dlg)
            show_toast("✏️ تم التعديل")
            render()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("تعديل المحتوى"),
            content=ft.Column(tight=True, width=300, controls=[title_field, image_field]),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: _close_dialog(page, dlg)),
                ft.ElevatedButton(
                    "حفظ", bgcolor=c("primary"), color=ft.Colors.WHITE, on_click=save_click
                ),
            ],
        )
        _open_dialog(page, dlg)

    # ============================================================
    # ADMIN CONTENT MANAGER (المواسم والحلقات)
    # ============================================================
    def open_admin_content_manager(cid):
        state["current_content_id"] = cid
        show_admin_content_manager_dialog()

    def show_admin_content_manager_dialog():
        item = find_content(state["current_content_id"])
        if not item:
            return
        seasons = item.get("seasons") or []

        new_season_field = ft.TextField(label="رقم الموسم", width=110, keyboard_type=ft.KeyboardType.NUMBER)

        async def add_season_click(e):
            try:
                num = int(new_season_field.value)
            except (TypeError, ValueError):
                num = 0
            if num < 1:
                show_toast("أدخل رقم موسم صحيح", "error")
                return
            if not item.get("seasons"):
                item["seasons"] = []
            if any(s["number"] == num for s in item["seasons"]):
                show_toast("هذا الموسم موجود مسبقاً", "error")
                return
            item["seasons"].append({"number": num, "episodes": []})
            item["seasons"].sort(key=lambda s: s["number"])
            await save_data()
            show_toast("تم إضافة الموسم")
            render()
            show_admin_content_manager_dialog()

        def delete_season(si):
            async def do_delete():
                item["seasons"].pop(si)
                await save_data()
                show_toast("تم حذف الموسم", "error")
                render()
                show_admin_content_manager_dialog()

            confirm_dialog("حذف الموسم", "حذف الموسم وجميع حلقاته؟", do_delete)

        def edit_season(si):
            num_field = ft.TextField(label="رقم الموسم الجديد", value=str(item["seasons"][si]["number"]))

            async def save_click(e):
                try:
                    num = int(num_field.value)
                except (TypeError, ValueError):
                    num = 0
                if num < 1:
                    show_toast("رقم غير صحيح", "error")
                    return
                if any(i != si and s["number"] == num for i, s in enumerate(item["seasons"])):
                    show_toast("رقم الموسم مستخدم", "error")
                    return
                item["seasons"][si]["number"] = num
                item["seasons"].sort(key=lambda s: s["number"])
                await save_data()
                _close_dialog(page, edlg)
                show_toast("تم التعديل")
                render()
                show_admin_content_manager_dialog()

            edlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("تعديل الموسم"),
                content=ft.Container(content=num_field, width=260),
                actions=[
                    ft.TextButton("إلغاء", on_click=lambda e: _close_dialog(page, edlg)),
                    ft.ElevatedButton("حفظ", bgcolor=c("primary"), color=ft.Colors.WHITE, on_click=save_click),
                ],
            )
            _open_dialog(page, edlg)

        def edit_episode(si, ei):
            ep = item["seasons"][si]["episodes"][ei]
            title_field = ft.TextField(label="عنوان الحلقة", value=ep.get("title") or "")
            url_field = ft.TextField(label="رابط الفيديو", value=ep.get("url") or "")

            async def save_click(e):
                new_title = (title_field.value or "").strip()
                ep["title"] = new_title or f"حلقة {ep['number']}"
                new_url = (url_field.value or "").strip()
                if new_url:
                    ep["url"] = new_url
                await save_data()
                _close_dialog(page, edlg)
                show_toast("تم التعديل")
                render()
                show_admin_content_manager_dialog()

            edlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("تعديل الحلقة"),
                content=ft.Column(tight=True, width=300, controls=[title_field, url_field]),
                actions=[
                    ft.TextButton("إلغاء", on_click=lambda e: _close_dialog(page, edlg)),
                    ft.ElevatedButton("حفظ", bgcolor=c("primary"), color=ft.Colors.WHITE, on_click=save_click),
                ],
            )
            _open_dialog(page, edlg)

        def delete_episode(si, ei):
            async def do_delete():
                item["seasons"][si]["episodes"].pop(ei)
                for idx, ep in enumerate(item["seasons"][si]["episodes"]):
                    ep["number"] = idx + 1
                await save_data()
                show_toast("تم حذف الحلقة", "error")
                render()
                show_admin_content_manager_dialog()

            confirm_dialog("حذف الحلقة", "حذف الحلقة؟", do_delete)

        season_blocks = []
        if not seasons:
            season_blocks.append(ft.Text("لا توجد مواسم", size=12, color=c("text_secondary")))
        else:
            for si, season in enumerate(seasons):
                ep_title_field = ft.TextField(label="عنوان الحلقة", dense=True, text_size=12, expand=1)
                ep_url_field = ft.TextField(label="رابط الفيديو", dense=True, text_size=12, expand=2)

                async def add_episode_click(e, si=si, tf=ep_title_field, uf=ep_url_field):
                    url = (uf.value or "").strip()
                    if not url:
                        show_toast("رابط الفيديو مطلوب", "error")
                        return
                    season_ = item["seasons"][si]
                    num = len(season_["episodes"]) + 1
                    title_ = (tf.value or "").strip()
                    season_["episodes"].append({"number": num, "title": title_ or f"حلقة {num}", "url": url})
                    await save_data()
                    show_toast("تم إضافة الحلقة")
                    render()
                    show_admin_content_manager_dialog()

                ep_rows = []
                for ei, ep in enumerate(season.get("episodes") or []):
                    ep_rows.append(
                        ft.Container(
                            padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                            bgcolor=c("bg"),
                            border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
                            border_radius=8,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        f"حلقة {ep['number']}: {ep.get('title') or ''}",
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=c("text"),
                                    ),
                                    ft.Row(
                                        spacing=2,
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.PLAY_ARROW,
                                                icon_color=ft.Colors.WHITE,
                                                bgcolor=c("success"),
                                                icon_size=14,
                                                on_click=lambda e, u=ep["url"]: play_click(e, u),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT,
                                                icon_color=ft.Colors.WHITE,
                                                bgcolor=c("warning"),
                                                icon_size=14,
                                                on_click=lambda e, si=si, ei=ei: edit_episode(si, ei),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE,
                                                icon_color=ft.Colors.WHITE,
                                                bgcolor=c("danger"),
                                                icon_size=14,
                                                on_click=lambda e, si=si, ei=ei: delete_episode(si, ei),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        )
                    )
                if not ep_rows:
                    ep_rows.append(ft.Text("لا توجد حلقات", size=11, color=c("text_secondary")))

                season_blocks.append(
                    ft.Container(
                        bgcolor=c("bg"),
                        border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
                        border_radius=10,
                        padding=10,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"الموسم {season['number']}",
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=c("text"),
                                        ),
                                        ft.Row(
                                            spacing=2,
                                            controls=[
                                                ft.IconButton(
                                                    icon=ft.Icons.EDIT,
                                                    icon_color=ft.Colors.WHITE,
                                                    bgcolor=c("warning"),
                                                    icon_size=14,
                                                    on_click=lambda e, si=si: edit_season(si),
                                                ),
                                                ft.IconButton(
                                                    icon=ft.Icons.DELETE,
                                                    icon_color=ft.Colors.WHITE,
                                                    bgcolor=c("danger"),
                                                    icon_size=14,
                                                    on_click=lambda e, si=si: delete_season(si),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Text("الحلقات", size=11, color=c("text_secondary")),
                                ft.Column(spacing=4, controls=ep_rows),
                                ft.Row(
                                    spacing=6,
                                    controls=[ep_title_field, ep_url_field,
                                              ft.IconButton(
                                                  icon=ft.Icons.ADD,
                                                  icon_color=ft.Colors.WHITE,
                                                  bgcolor=c("success"),
                                                  on_click=add_episode_click,
                                              )],
                                ),
                            ],
                        ),
                    )
                )

        content_col = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("المواسم", size=13, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                *season_blocks,
                ft.Row(
                    spacing=6,
                    controls=[
                        new_season_field,
                        ft.ElevatedButton(
                            "إضافة موسم",
                            icon=ft.Icons.ADD,
                            bgcolor=c("primary"),
                            color=ft.Colors.WHITE,
                            on_click=add_season_click,
                        ),
                    ],
                ),
            ],
        )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"⚙️ إدارة {item['title']}"),
            content=ft.Container(content=content_col, width=400, height=460),
            actions=[ft.TextButton("إغلاق", on_click=lambda e: (_close_dialog(page, dlg), render()))],
        )
        _open_dialog(page, dlg)

    # ============================================================
    # ADMIN: SETTINGS TAB ACTIONS
    # ============================================================
    async def publish_updates(e):
        await save_data()
        state["is_published"] = True
        await save_publish_status()
        show_toast("✅ تم حفظ ونشر التحديثات بنجاح!")
        render()

    def reset_data(e):
        async def do_reset():
            state["contents"] = []
            await save_data()
            show_toast("🗑️ تم إعادة التعيين")
            render()

        confirm_dialog("إعادة تعيين البيانات", "حذف جميع البيانات؟", do_reset)

    # ============================================================
    # ADMIN PANEL (تبويبات: إضافة / إدارة / إعدادات)
    # ============================================================
    def set_admin_tab(tab):
        state["admin_tab"] = tab
        render()

    def build_admin_tabs_bar():
        tabs = [("add", "إضافة"), ("manage", "إدارة"), ("settings", "إعدادات")]
        buttons = []
        for key, label in tabs:
            active = state["admin_tab"] == key
            buttons.append(
                ft.Container(
                    padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                    bgcolor=c("primary") if active else c("bg"),
                    border=ft.Border(left=ft.BorderSide(1, c("primary") if active else c("border")), top=ft.BorderSide(1, c("primary") if active else c("border")), right=ft.BorderSide(1, c("primary") if active else c("border")), bottom=ft.BorderSide(1, c("primary") if active else c("border"))),
                    border_radius=10,
                    on_click=lambda e, k=key: set_admin_tab(k),
                    content=ft.Text(
                        label, size=12, weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE if active else c("text"),
                    ),
                )
            )
        return ft.Row(spacing=6, controls=buttons, wrap=True)

    def build_admin_panel():
        if not state["admin_open"]:
            return ft.Container()

        if state["admin_tab"] == "add":
            tab_content = ft.Column(
                spacing=10,
                controls=[
                    ft.Text("إضافة محتوى جديد", size=14, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                    new_title_field,
                    new_image_field,
                    new_type_dropdown,
                    ft.ElevatedButton(
                        "إضافة",
                        icon=ft.Icons.SAVE,
                        bgcolor=c("primary"),
                        color=ft.Colors.WHITE,
                        width=10000,
                        on_click=add_content_click,
                    ),
                ],
            )
        elif state["admin_tab"] == "manage":
            tab_content = ft.Column(
                spacing=10,
                controls=[
                    ft.Text("قائمة المحتوى", size=14, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                    build_manage_list(),
                ],
            )
        else:
            status_dot_color = c("success") if state["is_published"] else c("warning")
            status_text = (
                f"تم النشر ({state['last_publish']})" if state["is_published"] else "لم يتم النشر بعد"
            )
            tab_content = ft.Column(
                spacing=10,
                controls=[
                    ft.Text("المظهر", size=14, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                    ft.OutlinedButton(
                        "تبديل الوضع الليلي",
                        icon=ft.Icons.DARK_MODE,
                        width=10000,
                        on_click=on_theme_toggle,
                    ),
                    ft.Divider(color=c("border")),
                    ft.Text("النشر", size=14, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                    ft.ElevatedButton(
                        "نشر التحديثات",
                        icon=ft.Icons.PUBLIC,
                        bgcolor=c("success"),
                        color=ft.Colors.WHITE,
                        width=10000,
                        on_click=publish_updates,
                    ),
                    ft.Container(
                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                        bgcolor=c("bg"),
                        border=ft.Border(left=ft.BorderSide(1, c("border")), top=ft.BorderSide(1, c("border")), right=ft.BorderSide(1, c("border")), bottom=ft.BorderSide(1, c("border"))),
                        border_radius=8,
                        content=ft.Row(
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=status_dot_color, border_radius=50),
                                ft.Text(status_text, size=12, color=c("text_secondary")),
                            ]
                        ),
                    ),
                    ft.Divider(color=c("border")),
                    ft.Text("البيانات", size=14, weight=ft.FontWeight.W_600, color=c("text_secondary")),
                    ft.ElevatedButton(
                        "إعادة تعيين البيانات",
                        icon=ft.Icons.DELETE_FOREVER,
                        bgcolor=c("danger"),
                        color=ft.Colors.WHITE,
                        width=10000,
                        on_click=reset_data,
                    ),
                ],
            )

        def close_admin(e):
            state["admin_open"] = False
            show_toast("تم إغلاق لوحة الإدارة")
            render()

        return ft.Container(
            bgcolor=c("bg_card"),
            border=ft.Border(left=ft.BorderSide(2, c("primary")), top=ft.BorderSide(2, c("primary")), right=ft.BorderSide(2, c("primary")), bottom=ft.BorderSide(2, c("primary"))),
            border_radius=14,
            padding=16,
            margin=ft.Margin(left=0, right=0, top=12, bottom=12),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.SETTINGS, color=c("primary")),
                                    ft.Text("لوحة الإدارة", size=16, weight=ft.FontWeight.W_700, color=c("primary")),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=ft.Colors.WHITE,
                                bgcolor=c("danger"),
                                icon_size=16,
                                on_click=close_admin,
                            ),
                        ],
                    ),
                    build_admin_tabs_bar(),
                    ft.Divider(color=c("border")),
                    tab_content,
                ],
            ),
        )

    # ============================================================
    # BOTTOM NAVIGATION
    # ============================================================
    def set_section(section):
        state["current_section"] = section
        render()

    def build_bottom_nav():
        items = [
            ("home", ft.Icons.HOME, "الرئيسية"),
            ("anime", ft.Icons.TV, "الأنمي"),
            ("cartoon", ft.Icons.CROP_LANDSCAPE, "كرتون"),
        ]
        controls = []
        for key, icon, label in items:
            active = state["current_section"] == key
            controls.append(
                ft.Container(
                    on_click=lambda e, k=key: set_section(k),
                    padding=ft.Padding(left=14, right=14, top=6, bottom=6),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Icon(icon, color=c("primary") if active else c("text_secondary"), size=22),
                            ft.Text(label, size=10, color=c("primary") if active else c("text_secondary")),
                        ],
                    ),
                )
            )
        return ft.Container(
            bgcolor=c("bottom_nav"),
            border=ft.Border(top=ft.BorderSide(1, c("border"))),
            padding=ft.Padding(left=0, right=0, top=6, bottom=6),
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=controls),
        )

    # ============================================================
    # MAIN RENDER
    # ============================================================
    def render():
        page.bgcolor = c("bg")

        query = state["search_query"]
        anime_list = [it for it in state["contents"] if it["type"] == "anime"]
        cartoon_list = [it for it in state["contents"] if it["type"] == "cartoon"]
        if query:
            anime_list = [it for it in anime_list if query in it["title"].lower()]
            cartoon_list = [it for it in cartoon_list if query in it["title"].lower()]

        sections = []
        show_anime = state["current_section"] in ("home", "anime")
        show_cartoon = state["current_section"] in ("home", "cartoon")

        if show_anime:
            sections.append(build_section(ft.Icons.TV, "الأنمي", anime_list, ft.Icons.MOVIE, "لا يوجد أنمي"))
        if show_cartoon:
            sections.append(
                ft.Container(height=10) if show_anime else ft.Container()
            )
            sections.append(
                build_section(ft.Icons.WORKSPACE_PREMIUM, "كرتون", cartoon_list, ft.Icons.WORKSPACE_PREMIUM, "لا يوجد كرتون")
            )

        main_container = ft.Container(
            padding=ft.Padding(left=14, right=14, top=12, bottom=20),
            expand=True,
            content=ft.Column(
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    build_search_bar(),
                    *sections,
                    build_admin_panel(),
                ],
            ),
        )

        root.controls = [
            build_header(),
            main_container,
            build_bottom_nav(),
        ]
        page.update()

    # =============================================
    # INIT
    # =============================================
    await load_data()
    await load_theme()
    await load_publish_status()
    page.bgcolor = c("bg")
    render()


if __name__ == "__main__":
    ft.app(target=main)