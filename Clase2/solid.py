# PRINCIPIOS SOLID

# S --> Single Responsibility --> Responsabilidad única
# Por ejemplo, en la clase hipoteca, solo se encarga de gestionar
# el amount, de quién viene... para decidir si se concede o no.
# Dejamos fuera aplicación de escritorio que usará el gestor para hablar con el cliente.
# Dejamos fuera transacciones entre cuentas del banco si la concedida.
# Notificaciones al cliente sobre el estado de su hipoteca...


# O --> Open / Closed --> Principio Abierto / Cerrado
# Las clases deben permitir extenderse fácilmente, y no están pensadas para modificarse.


# L --> Barbara Liskov --> Principio de sustitución de Liskov

class Bird:

    def __init__(self):
        pass

    def live(self):
        pass

class FlyingEntity:
    def __init__(self):
        pass

    def fly(self):
        pass


class Eagle(Bird, FlyingEntity):
    pass

class Crow(Bird, FlyingEntity):
    pass

class Penguin(Bird):
    pass

bird = FlyingEntity()
bird.fly()


# I - Interface Segregation - Segregación de la interfaz

# Clases abstractas:
from abc import ABC, abstractmethod

class Worker(ABC):

    @abstractmethod
    def work(self):
        pass

class LivingObject(ABC):

    @abstractmethod
    def rest(self):
        pass

class HumanWorker(Worker, LivingObject):
    pass

class RobotWorker(Worker):
    pass


# D - Inversión de dependencias

class ChannelProvider:

    def send_notification(self):
        pass

class SMSProvider(ChannelProvider):
    pass

class EmailProvider(ChannelProvider):
    pass

class NotificationCenter:

    def __init__(self, channel:ChannelProvider):
        self.notification_channel = channel
        self.notification_channel.send_notification()

# Enviar notificación:
email_provider = EmailProvider()
notification_center = NotificationCenter(email_provider)
