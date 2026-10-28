import sqlite3

# -------------------------------------------------------------
# 1. Preparación y Consulta (SELECT)
# -------------------------------------------------------------
conn = sqlite3.connect('practica_dml.db')
cursor = conn.cursor()

# Creación de la tabla 'vendedores'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ventas_totales REAL,
        zona TEXT,
        fecha_ingreso TEXT
    )
''')

# Limpiamos datos previos por si se ejecuta varias veces
cursor.execute('DELETE FROM vendedores')

# Registros iniciales
vendedores_iniciales = [
    ('Ana Pérez', 8500.0, 'Norte', '2023-01-15'),
    ('Carlos Gómez', 12000.0, 'Sur', '2022-11-20'),
    ('Sofía Ruiz', 9500.0, 'Norte', '2023-03-10'),
    ('Miguel Ángel', 6000.0, 'Este', '2023-05-01')
]

cursor.executemany('''
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES (?, ?, ?, ?)
''', vendedores_iniciales)
conn.commit()

print("--- 1. CONSULTA: VENDEDORES DE LA ZONA NORTE ---")
cursor.execute("SELECT nombre, ventas_totales FROM vendedores WHERE zona = 'Norte'")
for fila in cursor.fetchall():
    print(f"Nombre: {fila[0]} | Ventas Totales: {fila[1]}")

# -------------------------------------------------------------
# 2. Expansión (INSERT)
# -------------------------------------------------------------
print("\n--- 2. EXPANSIÓN DE DATOS (INSERT) ---")
# Inserción de dos nuevos vendedores individuales
cursor.execute("INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso) VALUES ('Lucía Fernández', 11200.0, 'Oeste', '2023-06-12')")
cursor.execute("INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso) VALUES ('Vendedor Test', 400.0, 'Norte', '2023-09-01')")

# INSERT INTO masivo de 3 registros en una sola sentencia
nuevos_masivos = [
    ('Pedro Infante', 4500.0, 'Sur', '2023-07-01'),
    ('Elena Torres', 13500.0, 'Norte', '2022-10-15'),
    ('Raúl Castro', 8900.0, 'Este', '2023-04-20')
]

cursor.executemany('''
    INSERT INTO vendedores (nombre, ventas_totales, zona, fecha_ingreso)
    VALUES (?, ?, ?, ?)
''', nuevos_masivos)
conn.commit()
print("Registros individuales y masivos insertados exitosamente.")
# -------------------------------------------------------------
# 3. Mantenimiento (UPDATE)
# -------------------------------------------------------------
print("\n--- 3. MANTENIMIENTO (UPDATE) ---")
# Actualizar al vendedor con id = 2 sumándole 500 unidades a sus ventas
cursor.execute("UPDATE vendedores SET ventas_totales = ventas_totales + 500 WHERE id = 2")

# Reto: Cambiar zona a 'Internacional' para vendedores con más de 10,000 en ventas
cursor.execute("UPDATE vendedores SET zona = 'Internacional' WHERE ventas_totales > 10000")
conn.commit()
print("Ventas actualizadas y reasignación de zona 'Internacional' completada.")
# -------------------------------------------------------------
# 4. Limpieza (DELETE) y Verificación final
# -------------------------------------------------------------
print("\n--- 4. LIMPIEZA (DELETE) Y VERIFICACIÓN ---")
cursor.execute("SELECT id FROM vendedores WHERE nombre = 'Vendedor Test'")
vendedor_test = cursor.fetchone()

if vendedor_test:
    test_id = vendedor_test[0]
    cursor.execute("DELETE FROM vendedores WHERE id = ?", (test_id,))
    conn.commit()
    print(f"Vendedor de prueba eliminado correctamente (ID: {test_id}).")

print("\n--- ESTADO FINAL DE LA TABLA VENDEDORES ---")
cursor.execute("SELECT id, nombre, ventas_totales, zona, fecha_ingreso FROM vendedores")
for fila in cursor.fetchall():
    print(f"ID: {fila[0]} | Nombre: {fila[1]} | Ventas: {fila[2]} | Zona: {fila[3]} | Ingreso: {fila[4]}")

conn.close()
