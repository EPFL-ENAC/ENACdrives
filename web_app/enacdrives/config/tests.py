"""

Setup db with :
~~~
. venv3/bin/activate
python enacdrives/manage.py migrate
~~~

Run these tests with :
~~~
python enacdrives/manage.py test enacdrives
~~~

"""

import copy

from django.test import TestCase, Client

from config import models as mo


class ClientFilterTest(TestCase):
    def setUp(self):
        default_data = dict(
            rank=1,
            enabled=True,
            category=mo.Config.CAT_ALL,
            name="{name}",
            client_filter_version="",
            client_filter_os="",
            client_filter_os_version="",
            data="[msg]\n" "name=data from {name}\n" "text=data from {name}",
        )

        def get_data(name, **args):
            data = copy.deepcopy(default_data)
            data["name"] = data["name"].format(name=name)
            data["data"] = data["data"].format(name=name)
            for k, v in args.items():
                data[k] = v
            return data

        mo.Config.objects.get_or_create(**get_data("conf1"))
        mo.Config.objects.get_or_create(
            **get_data("conf2", client_filter_version="0.9")
        )
        mo.Config.objects.get_or_create(
            **get_data("conf3", client_filter_version="<0.9")
        )
        mo.Config.objects.get_or_create(
            **get_data("conf4", client_filter_version=">=1.0.0")
        )
        mo.Config.objects.get_or_create(
            **get_data("conf5", client_filter_version=">1.0.0")
        )
        mo.Config.objects.get_or_create(
            **get_data("conf6", client_filter_os="Ubuntu-Linux")
        )
        mo.Config.objects.get_or_create(
            **get_data("conf7", client_filter_os="Apple-Darwin")
        )
        mo.Config.objects.get_or_create(
            **get_data(
                "conf8",
                client_filter_os="Ubuntu-Linux",
                client_filter_os_version=">=14.04",
            )
        )
        mo.Config.objects.get_or_create(
            **get_data(
                "conf9",
                client_filter_os="Ubuntu-Linux",
                client_filter_os_version="12.04",
            )
        )

        # for conf in mo.Config.objects.all():
        #     print("->\n{}".format(conf.pformat()))

    def test_get_config_version(self):
        c = Client()
        response = c.get(
            "/config/get",
            {
                "username": "bancal",
                "os": "foo",
                "os_version": "123",
                "version": "1.0.0",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(
            response.content.decode().strip(),
            "\n\n".join(
                [
                    "[msg]\nname=data from {id}\ntext=data from {id}".format(id=id)
                    for id in ("conf1", "conf4")
                ]
            ),
        )

    def test_get_config_os(self):
        c = Client()
        response = c.get(
            "/config/get",
            {
                "username": "bancal",
                "os": "Ubuntu-Linux",
                "os_version": "14.04",
                "version": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(
            response.content.decode().strip(),
            "\n\n".join(
                [
                    "[msg]\nname=data from {id}\ntext=data from {id}".format(id=id)
                    for id in ("conf1", "conf4", "conf5", "conf6", "conf8")
                ]
            ),
        )

    def test_get_config_os_version_1(self):
        c = Client()
        response = c.get(
            "/config/get",
            {
                "username": "bancal",
                "os": "Ubuntu-Linux",
                "os_version": "14.04",
                "version": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(
            response.content.decode().strip(),
            "\n\n".join(
                [
                    "[msg]\nname=data from {id}\ntext=data from {id}".format(id=id)
                    for id in ("conf1", "conf4", "conf5", "conf6", "conf8")
                ]
            ),
        )

    def test_get_config_os_version_2(self):
        c = Client()
        response = c.get(
            "/config/get",
            {
                "username": "bancal",
                "os": "Ubuntu-Linux",
                "os_version": "12.04",
                "version": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(
            response.content.decode().strip(),
            "\n\n".join(
                [
                    "[msg]\nname=data from {id}\ntext=data from {id}".format(id=id)
                    for id in ("conf1", "conf4", "conf5", "conf6", "conf9")
                ]
            ),
        )
