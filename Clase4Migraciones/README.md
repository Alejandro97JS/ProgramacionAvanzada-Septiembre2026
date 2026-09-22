# Clase 4 · Migraciones de base de datos con Alembic

## El caso de uso

La API de usuarios de `Clase4Peticiones` **ya está en producción** y tiene usuarios reales en la tabla `users`:

| id | username | email | age |
|----|----------|-------|-----|

Aparecen dos requisitos nuevos:

1. **Desactivar cuentas sin borrarlas** ("soft delete") y saber cuándo se registró cada usuario → nuevas columnas `is_active` y `created_at`, las dos **NOT NULL**.
2. **La edad guardada se queda desfasada**: quien se registró con 20 años seguirá teniendo 20 dentro de cinco años. Hay que guardar la **fecha de nacimiento** (`birth_date`) y calcular la edad al vuelo, **sin perder la edad de los usuarios que ya existen**.

### ¿Por qué no basta con lo que hacíamos hasta ahora?

- `Base.metadata.create_all()` **sólo crea las tablas que no existen**. Si `users` ya existe, no le añade ni le quita columnas. El código nuevo fallaría con `no such column: birth_date`.
- Borrar `usuarios.db` y volver a crearla **destruye los datos de producción**.
- Lanzar a mano `ALTER TABLE` en cada servidor (local, pruebas, producción…) no deja rastro: nadie sabe qué cambios tiene aplicados cada base de datos.

**Alembic** resuelve esto: cada cambio del esquema es un fichero Python (una *migración*) guardado en git, con un `upgrade()` para aplicarlo y un `downgrade()` para deshacerlo. La base de datos guarda en la tabla `alembic_version` en qué migración está, y Alembic sabe cuáles le faltan.

## Estructura

```
Clase4Migraciones/
├── alembic.ini                  # configuración de Alembic (generado con `alembic init`)
├── alembic/
│   ├── env.py                   # conecta Alembic con NUESTRA BD y NUESTROS modelos
│   ├── script.py.mako           # plantilla para las migraciones nuevas
│   └── versions/                # ← la historia del esquema, una migración por fichero
│       ├── 0001_crear_tabla_users.py        esquema inicial (id, username, email, age)
│       ├── 0002_is_active_y_created_at.py   columnas NOT NULL en una tabla con datos
│       └── 0003_age_a_birth_date.py         cambio de esquema + migración de DATOS
├── app/
│   ├── database.py              # engine, sesión y Base (una sola DATABASE_URL)
│   └── models.py                # modelo UserDB en su versión MÁS RECIENTE
├── main.py                      # API final; no arranca si la BD no está migrada
├── seed_datos.py                # mete usuarios "de producción" con el esquema 0001
├── ver_bd.py                    # enseña versión, columnas y filas de la BD
└── test_requests.py             # prueba la API final
```

## Paso a paso

Todos los comandos se lanzan **desde la carpeta `Clase4Migraciones/`** con el entorno virtual activado.

```powershell
cd Clase4Migraciones
..\env_clases_pontia\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 0 · Ver la historia de migraciones

```powershell
alembic history
```
```
0002 -> 0003 (head), Sustituir age por birth_date (migración de ESQUEMA + DATOS)
0001 -> 0002, Añadir is_active y created_at a users
<base> -> 0001, Crear tabla users (esquema inicial, el que ya estaba en producción)
```
Cada migración apunta a la anterior con `down_revision`, formando una cadena. `head` es la última.

### Paso 1 · Recrear la situación de producción (versión 0001)

```powershell
alembic upgrade 0001      # crea la tabla users como en Clase4Peticiones
python seed_datos.py      # mete 4 usuarios con su edad (age)
python ver_bd.py
```
```
Versión de la BD (tabla alembic_version): 0001
Columnas de users:  id, username, email, age
  {'id': 1, 'username': 'juan', ..., 'age': 20}
  ...
```

### Paso 2 · Añadir columnas NOT NULL a una tabla con datos (0002)

Lee antes `alembic/versions/0002_is_active_y_created_at.py`. Verás dos técnicas:
- `is_active` → `NOT NULL` + `server_default`: la BD rellena las filas antiguas.
- `created_at` → el patrón de 3 pasos: añadir como nullable → rellenar con `UPDATE` → pasar a NOT NULL.

```powershell
alembic upgrade 0002
python ver_bd.py          # las filas antiguas tienen is_active=1 y created_at relleno
```

### Paso 3 · Cambiar `age` por `birth_date` sin perder datos (0003)

Lee `alembic/versions/0003_age_a_birth_date.py`. Es la parte más importante: `--autogenerate` sólo habría escrito "crear `birth_date`, borrar `age`", **y se habrían perdido las edades**. La conversión de datos está escrita a mano.

```powershell
alembic upgrade head      # head = la última migración
python ver_bd.py          # ya no hay age; juan (20 años) tiene birth_date 2006-01-01
alembic current           # 0003 (head)
```

### Paso 4 · Arrancar la API y probarla

```powershell
uvicorn main:app --reload        # terminal 1
python test_requests.py          # terminal 2
```
Los usuarios antiguos aparecen con su `age` **calculada** a partir de `birth_date`, y `DELETE /users/{id}` sólo los desactiva.

### Paso 5 · Deshacer y rehacer

```powershell
alembic downgrade -1      # vuelve a la 0002: reaparece age, calculada desde birth_date
python ver_bd.py
uvicorn main:app          # ¡NO ARRANCA! "La BD está en la versión '0002' pero el código espera '0003'"
alembic upgrade head      # la dejamos otra vez al día
```
Que la API se niegue a arrancar es a propósito (`comprobar_migraciones()` en `main.py`): así nadie despliega código nuevo sobre una BD sin migrar.

### Paso 6 · Comprobar que modelos y migraciones coinciden

```powershell
alembic check             # "No new upgrade operations detected."
```
Si alguien cambia `app/models.py` y olvida crear la migración, `alembic check` falla. Es muy útil en CI.

Para empezar de cero en cualquier momento: borra `usuarios.db` y vuelve al paso 1.

## Cómo se crearon estos ficheros (el flujo real de trabajo)

Así montarías Alembic en tu propio proyecto:

1. **Inicializar Alembic** (una sola vez): `alembic init alembic`. Crea `alembic.ini` y la carpeta `alembic/`.
2. **Configurar `env.py`**: importar `DATABASE_URL` y `Base` de la app, `target_metadata = Base.metadata` y, con SQLite, `render_as_batch=True`.
3. **Por cada cambio del esquema**:
   1. Modificar el modelo en `app/models.py`.
   2. Generar el borrador: `alembic revision --autogenerate -m "descripción del cambio"`.
   3. **Revisar y corregir el fichero generado** en `alembic/versions/`: rellenar filas antiguas, convertir datos, completar el `downgrade()`…
   4. Probarlo en local: `alembic upgrade head`, luego `alembic downgrade -1` y otra vez `alembic upgrade head`.
   5. Hacer commit **del modelo y de la migración juntos**.
4. **Al desplegar**: `alembic upgrade head` en el servidor **antes** de arrancar la versión nueva de la API.

> Si la base de datos de producción ya existía (creada con `create_all`) antes de usar Alembic, no se ejecuta la migración inicial. Basta con `alembic stamp 0001` para decirle a Alembic que esa BD ya está en la 0001.

## Chuleta de comandos

| Comando | Qué hace |
|---|---|
| `alembic init alembic` | Crea la estructura de Alembic (una vez por proyecto) |
| `alembic revision --autogenerate -m "..."` | Genera un borrador de migración comparando modelos y BD |
| `alembic revision -m "..."` | Genera una migración vacía para escribirla a mano |
| `alembic upgrade head` | Aplica todas las migraciones pendientes |
| `alembic upgrade 0002` | Avanza hasta una revisión concreta |
| `alembic downgrade -1` | Deshace la última migración |
| `alembic downgrade base` | Deshace todas las migraciones |
| `alembic current` | Revisión en la que está la BD |
| `alembic history` | Lista de migraciones |
| `alembic upgrade head --sql` | Imprime el SQL sin ejecutarlo (modo offline) |
| `alembic stamp 0001` | Marca la BD con esa revisión sin ejecutar nada |
| `alembic check` | Falla si los modelos tienen cambios sin migración |

## Errores típicos

- **`UnicodeDecodeError` al lanzar alembic en Windows** → hay tildes o eñes en `alembic.ini`. Alembic lo lee con la codificación del sistema.
- **`table users already exists`** → la BD se creó con `create_all` y no con Alembic. Usa `alembic stamp`.
- **`Cannot add a NOT NULL column with default value NULL`** → falta `server_default` o el patrón de 3 pasos (ver la 0002).
- **Importar `app.models` dentro de una migración** → no lo hagas. El modelo cambia con el tiempo y la migración antigua dejaría de funcionar. Usa `sa.table(...)` (ver la 0003).
