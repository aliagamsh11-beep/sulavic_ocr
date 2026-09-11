from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window


class SulavicOCRApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.94, 0.90, 1)  # بيج فاتح

        layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20
        )

        title = Label(
            text='[b]Sulavic OCR[/b]',
            markup=True,
            font_size='32sp',
            color=(0.24, 0.17, 0.11, 1)
        )
        layout.add_widget(title)

        status = Label(
            text='التطبيق يعمل بنجاح!',
            font_size='20sp',
            color=(0.42, 0.55, 0.13, 1)
        )
        layout.add_widget(status)

        button = Button(
            text='اضغط هنا',
            font_size='18sp',
            size_hint=(1, 0.2),
            background_color=(0.54, 0.43, 0.28, 1)
        )
        button.bind(on_press=lambda x: setattr(
            status, 'text', 'تم الضغط! التطبيق يعمل.'
        ))
        layout.add_widget(button)

        return layout


if __name__ == '__main__':
    SulavicOCRApp().run()
