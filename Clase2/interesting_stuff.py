class Mortgage:

    def __init__(self, amount:int, client:str):
        self.amount = amount
        self.client = client
        self.approved = None

    def check_approved(self):
        if self.approved is None:
            print("Mortgage in process")
        elif self.approved:
            print("Mortgage approved")
        else:
            print("Mortgage not approved")

    def calculate_approval(self):
        if self.client == "Juan":
            self.approved = True
        elif self.amount > 2500000:
            self.approved = False
        else:
            self.approved = True



class ClientApplicationGestor:
    def session_with_client(self):
        amount = int(input("Enter the amount of the mortgage: "))
        client = input("Enter the client name: ")
        mortgage = Mortgage(amount, client)
        mortgage.calculate_approval()
        mortgage.check_approved()
        return mortgage


client_application_gestor = ClientApplicationGestor()
client_application_gestor.session_with_client()