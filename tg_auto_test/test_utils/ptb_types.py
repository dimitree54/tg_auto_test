from collections.abc import Callable

from telegram.ext import Application, ApplicationBuilder

BuildApplication = Callable[[ApplicationBuilder], Application]
