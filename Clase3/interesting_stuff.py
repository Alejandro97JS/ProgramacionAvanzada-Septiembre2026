# Ruff --> Escrito en Rust, pero pensado para código Python

# PRE-COMMIT
# Terminas el código --> Haces commit --> ruff check . --fix

value = "Juan"
any(vowel in value for vowel in ["a", "e", "i", "o", "u"])

for vowel in ["a", "e", "i", "o", "u"]:
    if vowel in value:
        return True

lambda value: any(vowel in value for vowel in ["a", "e", "i", "o", "u"])

def any_vowel(value:str):
    for vowel in ["a", "e", "i", "o", "u"]:
        if vowel in value:
            return True

# En el back, se suelen usar medidas de protección adicionales:
# - Validación de datos, similar al front
# - Throttling (admito x peticiones al día, minuto... para una IP)
# - Paginación, tareas asíncronas...
