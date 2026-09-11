# ═══════════════════════════════════════════════════════
# 📱 Sulavic OCR
# ═══════════════════════════════════════════════════════
import os
import time
import threading
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, StringProperty

try:
    from camera4kivy import Preview
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

from ocr_engine import OCREngine

# ─── الألوان ───
BG     = (0.961, 0.941, 0.902, 1)
PRIM   = (0.545, 0.435, 0.278, 1)
TXT    = (0.243, 0.173, 0.110, 1)
RES    = (0.420, 0.557, 0.137, 1)
WHITE  = (1, 1, 1, 1)
DARK   = (0.365, 0.275, 0.180, 1)
LIGHT  = (0.729, 0.647, 0.529, 1)


class RoundedButton(Button):
    bg_color_rgba = ListProperty([0.545, 0.435, 0.278, 1])

    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = WHITE
        self.font_size = sp(16)
        self.bold = True
        self.bind(pos=self._r, size=self._r, bg_color_rgba=self._r)

    def _r(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color_rgba)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])


class MainScreen(Screen):
    status = StringProperty("جاهز للتصوير")
    count_text = StringProperty("عدد الحروف: 0")
    time_text = StringProperty("وقت التحليل: --")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.engine = None
        self.result_text = ""
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # عنوان
        root.add_widget(Label(
            text='[b]Sulavic OCR[/b]', markup=True,
            font_size=sp(24), color=TXT,
            size_hint_y=None, height=dp(42)
        ))
        root.add_widget(Label(
            text='التعرف على الحروف السولافية القديمة',
            font_size=sp(12), color=TXT,
            size_hint_y=None, height=dp(22)
        ))

        # كاميرا
        cam_frame = FloatLayout(size_hint_y=0.42)
        with cam_frame.canvas.before:
            Color(*LIGHT)
            self.cam_bg = RoundedRectangle(
                pos=cam_frame.pos, size=cam_frame.size, radius=[dp(20)]
            )
        cam_frame.bind(
            pos=lambda *a: setattr(self.cam_bg, 'pos', cam_frame.pos),
            size=lambda *a: setattr(self.cam_bg, 'size', cam_frame.size)
        )

        if CAMERA_AVAILABLE:
            try:
                self.preview = Preview(
                    aspect_ratio=False,
                    size_hint=(0.95, 0.95),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )
                cam_frame.add_widget(self.preview)
            except Exception as e:
                print(f"Camera error: {e}")
                cam_frame.add_widget(Label(text='[ الكاميرا غير متوفرة ]', color=TXT))
        else:
            cam_frame.add_widget(Label(text='[ وضع بدون كاميرا ]', color=TXT))

        root.add_widget(cam_frame)

        # الحالة
        self.status_lbl = Label(
            text=self.status, font_size=sp(13), color=TXT,
            size_hint_y=None, height=dp(28)
        )
        root.add_widget(self.status_lbl)

        # النتائج
        res_frame = BoxLayout(orientation='vertical', size_hint_y=0.28, padding=dp(8))
        with res_frame.canvas.before:
            Color(*WHITE)
            self.res_bg = RoundedRectangle(
                pos=res_frame.pos, size=res_frame.size, radius=[dp(15)]
            )
        res_frame.bind(
            pos=lambda *a: setattr(self.res_bg, 'pos', res_frame.pos),
            size=lambda *a: setattr(self.res_bg, 'size', res_frame.size)
        )

        scroll = ScrollView()
        self.result_lbl = Label(
            text='لم يتم التحليل بعد',
            font_size=sp(18), color=RES, markup=True,
            size_hint_y=None, halign='center', valign='middle'
        )
        self.result_lbl.bind(
            width=lambda *a: setattr(self.result_lbl, 'text_size',
                                     (self.result_lbl.width, None)),
            texture_size=lambda *a: setattr(self.result_lbl, 'height',
                                            self.result_lbl.texture_size[1])
        )
        scroll.add_widget(self.result_lbl)
        res_frame.add_widget(scroll)
        root.add_widget(res_frame)

        # العدادات
        info = BoxLayout(size_hint_y=None, height=dp(28))
        self.count_lbl = Label(text=self.count_text, font_size=sp(12), color=TXT)
        self.time_lbl = Label(text=self.time_text, font_size=sp(12), color=TXT)
        info.add_widget(self.count_lbl)
        info.add_widget(self.time_lbl)
        root.add_widget(info)

        # أزرار
        row1 = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        b_capture = RoundedButton(text='📷 التقاط وتحليل')
        b_capture.bind(on_release=self.on_capture)
        row1.add_widget(b_capture)
        b_clear = RoundedButton(text='🔄 مسح', bg_color_rgba=DARK)
        b_clear.bind(on_release=self.on_clear)
        row1.add_widget(b_clear)
        root.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        b_save = RoundedButton(text='💾 حفظ', bg_color_rgba=RES)
        b_save.bind(on_release=self.on_save)
        row2.add_widget(b_save)
        b_share = RoundedButton(text='📤 مشاركة', bg_color_rgba=RES)
        b_share.bind(on_release=self.on_share)
        row2.add_widget(b_share)
        root.add_widget(row2)

        self.add_widget(root)

    def set_status(self, txt):
        def u(dt):
            self.status = txt
            self.status_lbl.text = txt
        Clock.schedule_once(u, 0)

    def on_capture(self, *a):
        if CAMERA_AVAILABLE and hasattr(self, 'preview'):
            try:
                self.preview.capture_photo()
                self.set_status("📸 تم التصوير — جاري التحليل...")
                Clock.schedule_once(self._find_and_process, 2.0)
            except Exception as e:
                self.set_status(f"❌ خطأ: {e}")
        else:
            self._demo()

    def _find_and_process(self, dt):
        dirs = [
            Path('/storage/emulated/0/DCIM'),
            Path('/storage/emulated/0/Pictures'),
            Path('.').resolve(),
        ]
        latest, lt = None, 0
        for d in dirs:
            if not d.exists():
                continue
            for f in d.rglob('*.jpg'):
                t = f.stat().st_mtime
                if t > lt:
                    lt, latest = t, f
        if latest:
            self._infer(str(latest))
        else:
            self.set_status("⚠️ لم يتم العثور على صورة")

    def _infer(self, path):
        def worker():
            start = time.time()
            if self.engine is None:
                mp = self._find_model()
                cp = self._find_classes()
                if mp:
                    self.engine = OCREngine(mp, cp)
                    self.engine.load()
            results = self.engine.predict(path) if (self.engine and self.engine.loaded) else []
            elapsed = time.time() - start
            Clock.schedule_once(lambda dt: self._show(results, elapsed), 0)
        threading.Thread(target=worker, daemon=True).start()

    def _find_model(self):
        for c in ['models/best.tflite', 'assets/best.tflite',
                  'best.tflite',
                  os.path.join(os.path.dirname(__file__), 'models', 'best.tflite'),
                  os.path.join(os.path.dirname(__file__), 'assets', 'best.tflite')]:
            if os.path.exists(c):
                return c
        return None

    def _find_classes(self):
        for c in ['classes.json',
                  os.path.join(os.path.dirname(__file__), 'classes.json')]:
            if os.path.exists(c):
                return c
        return None

    @mainthread
    def _show(self, results, elapsed):
        if not results:
            self.result_lbl.text = "لم يتم التعرف على حروف"
            self.result_text = ""
            self.count_lbl.text = "عدد الحروف: 0"
            self.time_lbl.text = f"وقت التحليل: {elapsed:.2f}s"
            self.set_status("✅ انتهى — لا نتائج")
            return
        line = ''.join(r['letter'] for r in results)
        details = "\n".join(f"• {r['letter']}  ({r['confidence']*100:.1f}%)"
                             for r in results)
        self.result_lbl.text = f"[b][size=28]{line}[/size][/b]\n\n{details}"
        self.result_text = line
        self.count_lbl.text = f"عدد الحروف: {len(results)}"
        self.time_lbl.text = f"وقت التحليل: {elapsed:.2f}s"
        self.set_status("✅ تم التعرف")

    def _demo(self):
        self.set_status("🧪 وضع تجريبي")
        demo = [
            {'letter': 'А', 'confidence': 0.95},
            {'letter': 'Б', 'confidence': 0.87},
            {'letter': 'В', 'confidence': 0.92},
        ]
        Clock.schedule_once(lambda dt: self._show(demo, 0.42), 1.2)

    def on_clear(self, *a):
        self.result_lbl.text = "لم يتم التحليل بعد"
        self.result_text = ""
        self.count_lbl.text = "عدد الحروف: 0"
        self.time_lbl.text = "وقت التحليل: --"
        self.set_status("🧹 تم المسح")

    def on_save(self, *a):
        if not self.result_text:
            self.set_status("⚠️ لا نتيجة للحفظ")
            return
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            if platform == 'android':
                fn = f"/storage/emulated/0/sulavic_{ts}.txt"
            else:
                fn = f"sulavic_{ts}.txt"
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(self.result_text)
            self.set_status(f"💾 تم الحفظ: {os.path.basename(fn)}")
        except Exception as e:
            self.set_status(f"❌ فشل: {e}")

    def on_share(self, *a):
        if not self.result_text:
            self.set_status("⚠️ لا نتيجة للمشاركة")
            return
        if platform != 'android':
            self.set_status("📤 للمشاركة على أندرويد فقط")
            return
        try:
            from jnius import autoclass, cast
            A = autoclass('org.kivy.android.PythonActivity')
            I = autoclass('android.content.Intent')
            S = autoclass('java.lang.String')
            it = I()
            it.setAction(I.ACTION_SEND)
            it.putExtra(I.EXTRA_TEXT, self.result_text)
            it.setType("text/plain")
            ch = I.createChooser(it, cast('java.lang.CharSequence', S("مشاركة")))
            A.mActivity.startActivity(ch)
            self.set_status("📤 تم فتح المشاركة")
        except Exception as e:
            self.set_status(f"❌ فشل: {e}")


class SulavicOCRApp(App):
    def build(self):
        self.title = 'Sulavic OCR'
        Window.clearcolor = BG
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.CAMERA,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ])
            except Exception as e:
                print(f"permissions: {e}")


if __name__ == '__main__':
    SulavicOCRApp().run()
