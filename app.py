from __future__ import annotations
from nicegui import ui
import macvendor


if __name__ in {'__main__', '__mp_main__'}:
    APP_NAME = 'MAC VENDOR'
    VENDOR_ERROR = 'Неизвестный вендор'
    ui.add_head_html('<style>body {background-color: #EEE; }</style>')
    ui.button.default_classes('bg-gray-100 w-26')
    ui.button.default_props('flat')
    with ui.row() as row:
        row.classes('w-full absolute-full justify-center items-center')
        with ui.card(
            align_items='center'
        ).props('flat bordered').classes('w-96'):
            ui.label(APP_NAME).classes(
                'w-full text-center text-base bg-primary text-white py-2 px-4'
            )
            address = ui.input().classes('w-full text-4xl')
            address.props(
                'outlined autofocus input-style="text-align: center"'
            )
            ui.on('clipboard', lambda e: address.set_value(e.args))
            with ui.row().classes('w-full justify-between'):
                ui.button('Вставить').on(
                    'click',
                    js_handler='''
                        async () => emitEvent(
                            "clipboard", await navigator.clipboard.readText()
                        )
                    ''')
                ui.button(
                    'Найти',
                    on_click=lambda: vendor.set_text(
                        macvendor.lookup(address.value)
                    )
                )
                ui.button(
                    'Очистить',
                    on_click=lambda: (
                        address.set_value(None),
                        address.run_method('focus'),
                        vendor.set_text(VENDOR_ERROR)
                    )
                )
            vendor = ui.label(VENDOR_ERROR)
            vendor.classes('w-full bg-gray-100 text-base text-center py-2 px-4')
    ui.run(title=APP_NAME)
