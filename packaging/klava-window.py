#!/usr/bin/env python3
"""Klava в отдельном окне на системном WebKitGTK (GTK 4, WebKit 6.0).

Запуск:  klava-window.py             — открыть окно
         klava-window.py --selftest  — загрузить страницу без окна, проверить и выйти
"""
import json
import os
import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gio, GLib, Gtk, WebKit  # noqa: E402

APP_ID = 'io.github.alexander_lun.Klava'
APP_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
INDEX = os.path.join(APP_DIR, 'index.html')
# Данные страницы (localStorage) — вне каталога приложения, чтобы не мешать git
DATA_DIR = os.path.join(GLib.get_user_data_dir(), 'klava-data')
CACHE_DIR = os.path.join(GLib.get_user_cache_dir(), 'klava')

SELFTEST_JS = """
(() => {
  localStorage.setItem('klava-selftest', '1');
  const ok = localStorage.getItem('klava-selftest') === '1';
  localStorage.removeItem('klava-selftest');
  return JSON.stringify({
    title: document.title,
    keys: document.querySelectorAll('#kbd .key').length,
    classicsRu: (window.CLASSICS_RU || []).length,
    classicsEn: (window.CLASSICS_EN || []).length,
    localStorage: ok,
    text: (document.querySelector('#text') || {}).textContent.length
  });
})()
"""


class Klava(Gtk.Application):
    def __init__(self, selftest=False):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE if selftest else Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.selftest = selftest
        self.result = 1

    def do_startup(self):
        Gtk.Application.do_startup(self)
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', lambda *a: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action('app.quit', ['<Control>q'])

    def do_activate(self):
        win = self.props.active_window
        if win:
            win.present()
            return
        session = WebKit.NetworkSession.new(DATA_DIR, CACHE_DIR)
        session.connect('download-started', self.on_download)
        view = WebKit.WebView(network_session=session)
        view.get_settings().set_enable_developer_extras(False)
        view.connect('load-changed', self.on_load)
        view.connect('decide-policy', self.on_policy)

        win = Gtk.ApplicationWindow(application=self, title='Klava', default_width=1280, default_height=880)
        win.set_icon_name('klava')
        win.set_child(view)
        view.load_uri(Gio.File.new_for_path(INDEX).get_uri())
        if self.selftest:
            GLib.timeout_add_seconds(30, self.on_timeout)
        else:
            win.present()

    # Экспорт статистики: сохраняем в «Загрузки» без лишних вопросов
    def on_download(self, session, download):
        def decide(dl, name):
            folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD) or GLib.get_home_dir()
            dl.set_destination(os.path.join(folder, name or 'klava-stats.json'))
            return True
        download.connect('decide-destination', decide)

    # Внешние ссылки открываем в обычном браузере, а не внутри тренажёра
    def on_policy(self, view, decision, decision_type):
        if decision_type != WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            return False
        uri = decision.get_navigation_action().get_request().get_uri()
        if uri.startswith(('http://', 'https://')):
            Gio.AppInfo.launch_default_for_uri(uri, None)
            decision.ignore()
            return True
        return False

    def on_load(self, view, event):
        if self.selftest and event == WebKit.LoadEvent.FINISHED:
            view.evaluate_javascript(SELFTEST_JS, -1, None, None, None, self.on_selftest)

    def on_selftest(self, view, res):
        try:
            data = json.loads(view.evaluate_javascript_finish(res).to_string())
            print(json.dumps(data, ensure_ascii=False))
            good = data['keys'] > 50 and data['classicsRu'] > 0 and data['classicsEn'] > 0 and data['localStorage'] and data['text'] > 0
            self.result = 0 if good else 1
        except GLib.Error as e:
            print('selftest error:', e.message, file=sys.stderr)
        self.quit()

    def on_timeout(self):
        print('selftest: page did not load in 30 s', file=sys.stderr)
        self.quit()
        return False


def main():
    selftest = '--selftest' in sys.argv
    app = Klava(selftest)
    app.run([sys.argv[0]])
    return app.result if selftest else 0


if __name__ == '__main__':
    sys.exit(main())
