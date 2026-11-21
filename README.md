# Beagle Games

Beagle Games es una tienda demostrativa de videojuegos. Ayuda a explorar un catálogo, encontrar juegos por nombre, género, precio o requisitos de PC, y elegir títulos que se ajusten a un presupuesto. Resuelve el problema de comparar opciones de forma rápida en un solo lugar.

La compra es simulada: no procesa dinero ni solicita datos personales o bancarios. Todos los precios están expresados en COP como valores de referencia para este proyecto académico; no son cotizaciones verificadas de una tienda.

## Funcionalidades

- Catálogo de 86 videojuegos con portada, género, nivel de requisitos y precio positivo.
- Búsqueda por título, filtro por género y ordenamiento por nombre o precio.
- Recomendador que recibe género, perfil de PC y presupuesto, y devuelve hasta cinco juegos compatibles.
- Carrito de sesión que conserva juegos seleccionados, calcula el total y permite quitar artículos.
- Pago simulado que genera un comprobante descargable como PNG o PDF.
- Validación de juegos inexistentes, presupuestos fuera del rango permitido y carrito vacío.

## Tecnologías

| Tecnología | Uso | Motivo |
| --- | --- | --- |
| Python | Catálogo y lógica del recomendador | Permite organizar y probar la lógica en funciones pequeñas. |
| FastAPI | Rutas, formularios, validación y respuestas | Conecta las acciones de la página con la lógica del proyecto. |
| Jinja2 | Plantillas HTML dinámicas | Muestra el catálogo, las recomendaciones, el carrito y el comprobante con datos de Python. |
| Starlette SessionMiddleware | Sesión del carrito y del comprobante | Conserva el estado de la compra entre solicitudes sin requerir una base de datos. |
| pytest y TestClient | Pruebas de funciones y rutas | Comprueba los flujos principales sin depender de un navegador o un servicio externo. |
| html2canvas y html2pdf.js | Descarga PNG y PDF | Convierte el comprobante HTML mostrado en el navegador a formatos descargables. |
| HTML y CSS | Interfaz adaptable | Presenta la tienda en pantallas de escritorio y móviles. |

## Organización del proyecto

```text
app/
  catalog.py              Datos del catálogo y lógica del recomendador
  main.py                 Aplicación FastAPI, rutas, carrito y pago simulado
  templates/index.html    Plantilla Jinja2 de la tienda
  static/styles.css       Estilos de la página
  static/catalog.css      Estilos de búsqueda y ordenamiento
  static/receipt.js       Descargas del comprobante en PNG y PDF
  static/covers/          Portadas optimizadas extraídas del documento de trabajo
tests/
  test_app.py             Pruebas automatizadas con pytest
evidencias/
  catalogo.png            Página principal y catálogo
  recomendador.png        Recomendaciones tras enviar el formulario
  comprobante.png         Comprobante de una compra simulada
  pytest.png              Captura del resultado de las pruebas
  pruebas.txt             Registro de texto de pytest
requirements.txt          Dependencias para instalar y ejecutar el proyecto
```

Las rutas se encuentran en `app/main.py`. Los datos y la función `recommend_games` están en `app/catalog.py`; la interfaz dinámica se define en `app/templates/index.html` y los recursos estáticos se sirven desde `app/static/`.

## Recorrido de la información

1. El navegador envía una búsqueda o filtro a la ruta `GET /`; FastAPI filtra y ordena los títulos y Jinja2 renderiza las tarjetas.
2. El formulario del recomendador envía género, perfil del PC y presupuesto a `POST /recomendar`. La lógica compara esos valores con el catálogo y devuelve hasta cinco coincidencias. Si el presupuesto es inválido, la página muestra un mensaje.
3. El botón de una tarjeta envía su identificador a `POST /carrito/agregar/{game_id}`. FastAPI comprueba que exista y guarda su identificador en la sesión.
4. La ruta `POST /pagar` calcula la suma de precios, prepara una referencia y un comprobante, y vacía el carrito. El comprobante muestra los juegos y el total; la compra no genera un cobro real.
5. Si se intenta agregar un juego inexistente o pagar con el carrito vacío, la página informa que no puede completar la acción.

## Instalación y ejecución

Se requiere Python 3.10 o posterior.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

### macOS o Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre <http://127.0.0.1:8000>. Usa el buscador y los filtros del catálogo, agrega juegos con el botón `+`, y selecciona **Pagar ahora** para ver el comprobante simulado. En **Beagle Picker**, elige género, nivel de PC y presupuesto para recibir recomendaciones.

Las librerías de exportación del comprobante se cargan desde CDN al mostrar una compra. Se necesita conexión a internet para descargar PNG o PDF; el resto de la aplicación funciona localmente.

## Pruebas automatizadas

Ejecuta todas las pruebas desde la carpeta raíz:

```bash
python -m pytest -q
```

| Prueba | Datos utilizados | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| Recomendador | RPG, requisitos bajos, $60.000 COP | Solo devuelve RPG de requisitos bajos que respeten el presupuesto | Correcto; prueba aprobada |
| Ruta del catálogo | `GET /` | HTTP 200 y catálogo renderizado | HTTP 200; prueba aprobada |
| Recursos estáticos | CSS de la página y del catálogo | Ambos archivos responden HTTP 200 | Correcto; prueba aprobada |
| Portadas | Ruta de portada de cada juego | Las 86 responden HTTP 200 como JPEG | Correcto; prueba aprobada |
| Precios del catálogo | Tarjetas de los 86 juegos | Cada tarjeta muestra su precio positivo en COP | Correcto; prueba aprobada |
| Búsqueda y género | Género Aventura y búsqueda `Firewatch` | Muestra Firewatch, no Machinarium, y cuenta un resultado | Correcto; prueba aprobada |
| Ordenamiento | `sort=price_asc` | Las tarjetas siguen precio ascendente y nombre como desempate | Correcto; prueba aprobada |
| Carrito y pago | Stardew Valley ($60.000) y Undertale ($40.000) | Comprobante por $100.000 COP y carrito vacío | Correcto; prueba aprobada |
| Juego inválido | Identificador `no-es-un-juego` | Muestra aviso y no agrega un artículo | Correcto; prueba aprobada |
| Presupuesto inválido | Recomendador con presupuesto `-1` | Muestra el error de presupuesto | Correcto; prueba aprobada |
| Integridad del catálogo | Identificadores y precios de todos los juegos | IDs únicos y precios mayores que cero | Correcto; prueba aprobada |

Última ejecución registrada: **11 pruebas aprobadas**. pytest muestra además un aviso de deprecación de Starlette relacionado con `httpx` y `TestClient`; no afecta el resultado de las pruebas.

## Evidencias

- [Interfaz principal y catálogo](evidencias/catalogo.png)
- [Recomendador con resultados](evidencias/recomendador.png)
- [Comprobante de compra simulada](evidencias/comprobante.png)
- [Resultado de pytest](evidencias/pytest.png)
- [Registro de texto de pytest](evidencias/pruebas.txt)

## Conclusiones

Uno de los desafíos fue conservar los juegos elegidos entre las distintas solicitudes sin agregar una base de datos. Se resolvió usando sesiones firmadas para guardar el carrito y una referencia de la compra. Otro desafío fue asociar las portadas del documento de trabajo con los títulos correctos y reducir su tamaño; las imágenes se asignaron desde el catálogo y se optimizaron antes de servirlas.

El proyecto permitió practicar cómo FastAPI recibe y valida formularios, cómo Jinja2 representa resultados a partir de datos de Python y cómo pytest verifica funciones y rutas. También mostró la importancia de probar casos inválidos, como un presupuesto negativo o un identificador que no existe.
