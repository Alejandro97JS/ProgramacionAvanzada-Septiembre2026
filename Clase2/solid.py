# PRINCIPIOS SOLID
#
# S: Single Responsibility Principle
# O: Open/Closed Principle
# L: Liskov Substitution Principle
# I: Interface Segregation Principle
# D: Dependency Inversion Principle
#
# Partimos de Mortgage / ClientApplicationGestor (interesting_stuff.py).
# Preguntas distintas por principio:
#   S -> ¿esta clase hace demasiadas cosas?
#   O -> ¿para añadir algo nuevo tengo que reescribir código viejo?
#   L -> ¿puedo sustituir la clase base por una subclase sin romper al cliente?
#   I -> ¿el cliente depende de métodos que no usa?
#   D -> ¿el módulo de alto nivel depende de detalles concretos?

from typing import Protocol


# ---------------------------------------------------------------------------
# S: Single Responsibility Principle
# Una clase debe tener una sola razón para cambiar.
# ---------------------------------------------------------------------------

# MAL (rompe S): Mortgage mezcla datos, reglas de aprobación, UI por consola
# e incluso la sesión con el cliente.
class MortgageBadS:
    def __init__(self, amount: int, client: str):
        self.amount = amount
        self.client = client
        self.approved = None

    def calculate_approval(self):
        if self.client == "Juan":
            self.approved = True
        elif self.amount > 2500000:
            self.approved = False
        else:
            self.approved = True

    def check_approved(self):
        if self.approved is None:
            print("Mortgage in process")
        elif self.approved:
            print("Mortgage approved")
        else:
            print("Mortgage not approved")

    def ask_client_data(self):
        # Responsabilidad de interacción con el usuario (no de Mortgage)
        self.amount = int(input("Enter the amount of the mortgage: "))
        self.client = input("Enter the client name: ")


# BIEN (cumple S): cada clase tiene una sola responsabilidad.
class Mortgage:
    """Responsabilidad: representar una hipoteca (datos + estado)."""

    def __init__(self, amount: int, client: str):
        self.amount = amount
        self.client = client
        self.approved = None


class MortgageApprover:
    """Responsabilidad: decidir si la hipoteca se aprueba."""

    def calculate_approval(self, mortgage: Mortgage) -> None:
        if mortgage.client == "Juan":
            mortgage.approved = True
        elif mortgage.amount > 2500000:
            mortgage.approved = False
        else:
            mortgage.approved = True


class MortgageReporter:
    """Responsabilidad: comunicar el estado de la hipoteca."""

    def check_approved(self, mortgage: Mortgage) -> None:
        if mortgage.approved is None:
            print("Mortgage in process")
        elif mortgage.approved:
            print("Mortgage approved")
        else:
            print("Mortgage not approved")


class ClientApplicationGestor:
    """Responsabilidad: orquestar la sesión con el cliente."""

    def __init__(self, approver: MortgageApprover, reporter: MortgageReporter):
        self.approver = approver
        self.reporter = reporter

    def session_with_client(self) -> Mortgage:
        amount = int(input("Enter the amount of the mortgage: "))
        client = input("Enter the client name: ")
        mortgage = Mortgage(amount, client)
        self.approver.calculate_approval(mortgage)
        self.reporter.check_approved(mortgage)
        return mortgage


# ---------------------------------------------------------------------------
# O: Open/Closed Principle
# Abierto a extensión, cerrado a modificación.
# Puedes añadir comportamiento nuevo sin editar el código que ya funciona.
# ---------------------------------------------------------------------------

# MAL (rompe O): cada regla nueva obliga a modificar calculate_approval
# (otro if / elif). El código "viejo" nunca queda cerrado.
class MortgageApproverBadO:
    def calculate_approval(self, mortgage: Mortgage) -> None:
        if mortgage.client == "Juan":
            mortgage.approved = True
        elif mortgage.amount > 2500000:
            mortgage.approved = False
        # Mañana: elif credit_score < 600: ...
        # Pasado: elif country == "ES": ...
        # -> hay que tocar este método otra vez (viola O)
        else:
            mortgage.approved = True


# BIEN (cumple O): nuevas reglas = nuevas clases. MortgageApprover no se toca.
class ApprovalRule:
    def decide(self, mortgage: Mortgage) -> bool | None:
        """
        True  -> aprueba
        False -> rechaza
        None  -> esta regla no decide; pasa a la siguiente
        """
        raise NotImplementedError


class JuanAlwaysApprovedRule(ApprovalRule):
    def decide(self, mortgage: Mortgage) -> bool | None:
        if mortgage.client == "Juan":
            return True
        return None


class MaxAmountRule(ApprovalRule):
    def __init__(self, max_amount: int = 2_500_000):
        self.max_amount = max_amount

    def decide(self, mortgage: Mortgage) -> bool | None:
        if mortgage.amount > self.max_amount:
            return False
        return None


class DefaultApproveRule(ApprovalRule):
    def decide(self, mortgage: Mortgage) -> bool | None:
        return True


class ExtensibleMortgageApprover:
    """
    Cerrado a modificación: este código no cambia cuando llega una regla nueva.
    Abierto a extensión: se añade otra subclase de ApprovalRule a la lista.
    """

    def __init__(self, rules: list[ApprovalRule]):
        self.rules = rules

    def calculate_approval(self, mortgage: Mortgage) -> None:
        for rule in self.rules:
            decision = rule.decide(mortgage)
            if decision is not None:
                mortgage.approved = decision
                return


# Ejemplo de extensión SIN modificar ExtensibleMortgageApprover:
class MinAmountRule(ApprovalRule):
    def __init__(self, min_amount: int = 10_000):
        self.min_amount = min_amount

    def decide(self, mortgage: Mortgage) -> bool | None:
        if mortgage.amount < self.min_amount:
            return False
        return None


# ---------------------------------------------------------------------------
# L: Liskov Substitution Principle
# Si el código espera una clase base, debe poder usar cualquier subclase
# sin sorpresas: mismo contrato, mismas garantías.
# ---------------------------------------------------------------------------

# Contrato de ApprovalRule.decide:
#   - recibe un Mortgage
#   - devuelve True / False / None
#   - no exige atributos extra ni lanza errores "normales"

# MAL (rompe L): la subclase no es sustituible.
# ExtensibleMortgageApprover espera ApprovalRule, pero esta regla:
#   1) exige credit_score (Mortgage no lo tiene) -> AttributeError
#   2) lanza excepción en lugar de devolver True/False/None
class CreditScoreRuleBadL(ApprovalRule):
    def decide(self, mortgage: Mortgage) -> bool | None:
        # Rompe el contrato: asume un atributo que la base no promete.
        if mortgage.credit_score < 600:  # type: ignore[attr-defined]
            raise ValueError("Credit score too low")
        return True


# MAL (rompe L) también con herencia de Mortgage:
# El cliente espera poder crear Mortgage(amount, client) y marcar approved.
# FixedRateMortgage cambia el contrato (rechaza amount variables / rompe approved).
class FixedRateMortgageBadL(Mortgage):
    def __init__(self, client: str):
        # Precondición más fuerte: ya no acepta amount como la clase base.
        super().__init__(amount=200_000, client=client)
        self.rate = 0.03

    @property
    def approved(self):
        return True

    @approved.setter
    def approved(self, value):
        # Postcondición más débil: ignora la decisión del Approver.
        pass


def process_mortgage(mortgage: Mortgage, approver: ExtensibleMortgageApprover) -> None:
    """Cliente que solo conoce el tipo base Mortgage."""
    approver.calculate_approval(mortgage)
    # Confía en que mortgage.approved refleja la decisión de las reglas.


# BIEN (cumple L): subclases que respetan el contrato del padre.
class VariableRateMortgage(Mortgage):
    """Sigue siendo un Mortgage usable en cualquier sitio que espere Mortgage."""

    def __init__(self, amount: int, client: str, rate: float):
        super().__init__(amount, client)
        self.rate = rate


class CreditScoreRuleGoodL(ApprovalRule):
    """
    Respeta el contrato: si no hay score, no decide (None).
    No lanza; no exige atributos obligatorios en Mortgage.
    """

    def __init__(self, min_score: int = 600):
        self.min_score = min_score

    def decide(self, mortgage: Mortgage) -> bool | None:
        score = getattr(mortgage, "credit_score", None)
        if score is None:
            return None
        if score < self.min_score:
            return False
        return None


# ---------------------------------------------------------------------------
# I: Interface Segregation Principle
# Mejor varias interfaces pequeñas que una "gorda".
# Un cliente no debe verse obligado a depender de métodos que no usa.
# ---------------------------------------------------------------------------


# MAL (rompe I): interfaz gorda. Quien solo quiere aprobar o solo reportar
# tiene que conocer (e implementar) todo el catálogo.
class MortgageOperationsBadI(Protocol):
    def calculate_approval(self, mortgage: Mortgage) -> None: ...
    def check_approved(self, mortgage: Mortgage) -> None: ...
    def send_email(self, mortgage: Mortgage) -> None: ...
    def generate_pdf(self, mortgage: Mortgage) -> None: ...
    def calculate_interest(self, mortgage: Mortgage) -> float: ...


class FatMortgageServiceBadI:
    """Una sola clase/interfaz con demasiados métodos para todos los clientes."""

    def calculate_approval(self, mortgage: Mortgage) -> None:
        mortgage.approved = mortgage.amount <= 2_500_000

    def check_approved(self, mortgage: Mortgage) -> None:
        print("approved" if mortgage.approved else "not approved")

    def send_email(self, mortgage: Mortgage) -> None:
        print(f"Email sent to {mortgage.client}")

    def generate_pdf(self, mortgage: Mortgage) -> None:
        print(f"PDF generated for {mortgage.client}")

    def calculate_interest(self, mortgage: Mortgage) -> float:
        return mortgage.amount * 0.03


def console_flow_bad_i(ops: MortgageOperationsBadI, mortgage: Mortgage) -> None:
    # Solo necesita aprobar y reportar, pero el tipo le exige conocer email/pdf/interés.
    ops.calculate_approval(mortgage)
    ops.check_approved(mortgage)


# BIEN (cumple I): interfaces segregadas; cada cliente depende solo de lo suyo.
class Approver(Protocol):
    def calculate_approval(self, mortgage: Mortgage) -> None: ...


class Reporter(Protocol):
    def check_approved(self, mortgage: Mortgage) -> None: ...


class Notifier(Protocol):
    def send_email(self, mortgage: Mortgage) -> None: ...


class ConsoleApprover:
    def calculate_approval(self, mortgage: Mortgage) -> None:
        mortgage.approved = mortgage.amount <= 2_500_000


class ConsoleReporter:
    def check_approved(self, mortgage: Mortgage) -> None:
        if mortgage.approved:
            print("Mortgage approved")
        else:
            print("Mortgage not approved")


class EmailNotifier:
    def send_email(self, mortgage: Mortgage) -> None:
        print(f"Email sent to {mortgage.client}")


def console_flow_good_i(approver: Approver, reporter: Reporter, mortgage: Mortgage) -> None:
    # Solo depende de Approver + Reporter. No conoce Notifier ni PDF.
    approver.calculate_approval(mortgage)
    reporter.check_approved(mortgage)


def notify_if_approved(notifier: Notifier, mortgage: Mortgage) -> None:
    # Otro cliente: solo Notifier. No se ve forzado a implementar approve/report.
    if mortgage.approved:
        notifier.send_email(mortgage)


# ---------------------------------------------------------------------------
# D: Dependency Inversion Principle
# Los módulos de alto nivel no deben depender de detalles concretos.
# Ambos deben depender de abstracciones (Protocol / interfaz).
# ---------------------------------------------------------------------------

# MAL (rompe D): el gestor (alto nivel) instancia y conoce implementaciones
# concretas (bajo nivel). Cambiar de consola a email obliga a editar el gestor.
class ClientApplicationGestorBadD:
    def session_with_client(self, amount: int, client: str) -> Mortgage:
        mortgage = Mortgage(amount, client)
        # Dependencias concretas creadas aquí dentro:
        MortgageApprover().calculate_approval(mortgage)
        MortgageReporter().check_approved(mortgage)
        return mortgage


# BIEN (cumple D): el gestor depende de Approver / Reporter (abstracciones).
# Las implementaciones concretas se inyectan desde fuera.
class ClientApplicationGestorGoodD:
    def __init__(self, approver: Approver, reporter: Reporter):
        self.approver = approver
        self.reporter = reporter

    def session_with_client(self, amount: int, client: str) -> Mortgage:
        mortgage = Mortgage(amount, client)
        self.approver.calculate_approval(mortgage)
        self.reporter.check_approved(mortgage)
        return mortgage


class StrictApprover:
    """Otra implementación concreta intercambiable sin tocar el gestor."""

    def calculate_approval(self, mortgage: Mortgage) -> None:
        mortgage.approved = 50_000 <= mortgage.amount <= 1_000_000


class SilentReporter:
    def check_approved(self, mortgage: Mortgage) -> None:
        status = "approved" if mortgage.approved else "rejected"
        print(f"[silent] {mortgage.client}: {status}")


# ---------------------------------------------------------------------------
# Diferencia rápida (mismo dominio Mortgage)
# ---------------------------------------------------------------------------
# S: separar Mortgage / Approver / Reporter / Gestor
#    (una razón distinta para cambiar cada clase).
#
# O: dentro de la aprobación, no acumular ifs;
#    añadir reglas nuevas extendiendo ApprovalRule.
#
# L: esas subclases (reglas o tipos de hipoteca) deben poder sustituir
#    a la base sin romper a quien usa ApprovalRule / Mortgage.
#
# I: no obligar a un cliente a depender de una interfaz gorda;
#    Approver / Reporter / Notifier por separado.
#
# D: el gestor no crea ni conoce clases concretas;
#    recibe Approver/Reporter (abstracción) por inyección.


if __name__ == "__main__":
    # Demo O sin input: se puede extender la lista de reglas sin tocar el approver.
    mortgage = Mortgage(amount=5_000, client="Ana")
    approver = ExtensibleMortgageApprover(
        rules=[
            JuanAlwaysApprovedRule(),
            MinAmountRule(min_amount=10_000),  # extensión nueva
            MaxAmountRule(),
            DefaultApproveRule(),
        ]
    )
    reporter = MortgageReporter()

    approver.calculate_approval(mortgage)
    reporter.check_approved(mortgage)

    # Demo L: VariableRateMortgage sustituye a Mortgage sin romper process_mortgage.
    print("--- Liskov demo ---")
    variable = VariableRateMortgage(amount=150_000, client="Lucia", rate=0.035)
    variable.credit_score = 720  # opcional; CreditScoreRuleGoodL lo tolera
    liskov_approver = ExtensibleMortgageApprover(
        rules=[
            CreditScoreRuleGoodL(),
            MaxAmountRule(),
            DefaultApproveRule(),
        ]
    )
    process_mortgage(variable, liskov_approver)
    reporter.check_approved(variable)

    # Demo I: cada flujo solo depende de la interfaz que necesita.
    print("--- Interface Segregation demo ---")
    segregada = Mortgage(amount=180_000, client="Mario")
    console_flow_good_i(ConsoleApprover(), ConsoleReporter(), segregada)
    notify_if_approved(EmailNotifier(), segregada)

    # Demo D: mismo gestor, distintas implementaciones inyectadas.
    print("--- Dependency Inversion demo ---")
    gestor_consola = ClientApplicationGestorGoodD(ConsoleApprover(), ConsoleReporter())
    gestor_estricto = ClientApplicationGestorGoodD(StrictApprover(), SilentReporter())
    gestor_consola.session_with_client(180_000, "Mario")
    gestor_estricto.session_with_client(20_000, "Ana")  # rechazada por StrictApprover
