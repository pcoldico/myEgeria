"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""

from startup_check import check_connection
from error_popup_app import ErrorPopupApp
from my_egeria import MyEgeria


def on_mount(self):
    ok, msg = check_connection()
    if not ok:
        # Show popup with OK -> exit
        app = ErrorPopupApp(msg)
        app.run()
        return 1
    # start main app
    MyEgeria().run()
    return 0

def main():
    return on_mount(self=None)\

if __name__ == "__main__":
    raise SystemExit(on_mount(self=None))
