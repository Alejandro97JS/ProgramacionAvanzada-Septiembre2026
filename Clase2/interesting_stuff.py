# Para llamar a métodos privados, hay una "trampa" que se llama Python "Name Mangling" --> NO USAR

# Métodos privados

class Mortgage:

    def __init__(self, amount:int, client:str):
        self.amount = amount
        self.client = client
        self.__status = "UNKOWN"
        self._calculate_approved() # Lo suyo es en un hilo independiente

    def check_approved(self):
        print(f"Señor gestor, informe al cliente de que la hipoteca es: {self.__status}")

    def _calculate_approved(self):
        # Cálculos muy pesados, tarda su tiempo.
        self.__status = "PROCESSING"
        if self.client == "Johnny Depp":
            self.__status = "CONCEDED"
        elif self.amount > 250000:
            self.__status = "DENIED"
        else:
            self.__status = "CONCEDED"

    def _prueba(self):
        pass # Método protegido pero a nivel de comunidad Python. 
    # El lenguaje Python no protege nada aquí.

    def get_status(self) -> str:
        return self.__status

    def _set_status(self, status):
        self.__status = status

class SpecialEventSeptemberMortgage(Mortgage):

    def _calculate_approved(self):
        self._set_status("CONCEDED")

class ClientNotification:

    def __init__(self, email:str):
        self.email = email

    def notify_mortgage(self, status):
        # Enviar email:
        print(f"<EMAIL> Estimado {self.email}, le informamos que su hipoteca está: {status}")

class GestorAplicacionCliente:

    def sesion_con_cliente(self):
        amount = int(input("¿De cuánto es la hipoteca?"))
        client = input("¿Cómo te llamas?")
        email = input("Dime tu email")
        if False: # Sería if current month es septiembre.
            mortgage = SpecialEventSeptemberMortgage(amount, client)
        else:
            mortgage = Mortgage(amount, client)
        mortgage.check_approved()
        notificator = ClientNotification(email)
        notificator.notify_mortgage(mortgage.get_status())



def main():
    # Llega el cliente
    gac = GestorAplicacionCliente()
    gac.sesion_con_cliente()

main()
