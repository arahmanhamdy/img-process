import svc.app as application
import svc.config as configuration


def get_app():
    return _Bootstrapper().get_app()


def start_app():
    _Bootstrapper().start_app()


class _Bootstrapper(object):

    def start_app(self):
        self._create_application()
        self._run_app()

    def get_app(self):
        self._create_application()
        return self._application

    def _create_application(self):
        self._config = configuration.get_config()
        self._application = application.create_app(self._config)

    def _run_app(self):
        self._application.run(
            host=self._config.get("HOST", "0.0.0.0"),
            port=self._config.get("PORT", 8080),
            debug=self._config.get('DEBUG', False),
        )
