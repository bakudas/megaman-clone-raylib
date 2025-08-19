# game/observer.py
from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """
    A interface do Observador (quem observa).
    """

    @abstractmethod
    def on_notify(self, event: str):
        """Recebe a notificação de um evento do Sujeito."""
        pass


class Subject:
    """
    A classe base do Sujeito (quem é observado).
    Fornece a funcionalidade de gerenciamento de observadores.
    """

    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        """Adiciona um observador à lista."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """Remove um observador da lista."""
        try:
            self._observers.remove(observer)
        except ValueError:
            # O observador não está na lista, ignora silenciosamente.
            pass

    def notify(self, event: str):
        """Notifica todos os observadores sobre um evento."""
        for observer in self._observers:
            observer.on_notify(event)
