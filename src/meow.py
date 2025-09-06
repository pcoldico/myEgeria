from pydantic import ValidationError
import os
user = os.environ.setdefault("EGERIA_USER", "erinoverview")
pwd = os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")

import pyegeria.config
import pyegeria._exceptions_new

try:


    s = pyegeria.config.get_app_config(".env")
    print("meow")
    # p = get_app_config()
    print(pyegeria.config.settings.Environment.pyegeria_config_directory)

    env = pyegeria.config.settings.Environment
    user = pyegeria.settings.User_Profile


    client = pyegeria.EgeriaTech(env.egeria_view_server, env.egeria_platform_url, user.user_name, user.user_pwd)
    client.create_egeria_bearer_token()
    print(client.get_platform_origin())
except ValidationError as e:
    pyegeria._exceptions_new.print_validation_error(e)
finally:
    client.close_session()
