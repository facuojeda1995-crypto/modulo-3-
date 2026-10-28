import sqlite3

# Conectamos (o creamos) la base de datos para las transacciones
conn = sqlite3.connect("practica_transacciones.db")
cursor = conn.cursor()

# Creamos las tablas necesarias: productos y el log de auditoría
cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        stock INTEGER NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER,
        cambio TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insertamos datos iniciales de prueba si la tabla está vacía
cursor.execute("SELECT COUNT(*) FROM productos")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO productos (nombre, stock) VALUES (?, ?)", [
        ("Laptop", 10),
        ("Mouse", 50),
        ("Teclado", 30)
    ])
    conn.commit()

print("--- ESTADO INICIAL DE LA TABLA PRODUCTOS ---")
cursor.execute("SELECT * FROM productos")
print(cursor.fetchall())


# ==========================================
# CASO 1: Transacción Exitosa (COMMIT)
# Principio ACID: Consistencia y Durabilidad
# ==========================================
try:
    print("\n--- CASO 1: Transacción Exitosa ---")
    # Iniciamos la transacción explícitamente
    cursor.execute("BEGIN TRANSACTION;")
    
    # 1. Reducir el stock del producto 1 (Laptop)
    cursor.execute("UPDATE productos SET stock = stock - 2 WHERE id = 1;")
    
    # 2. Registrar el cambio en la tabla de auditoría (ventas_log)
    cursor.execute("INSERT INTO ventas_log (producto_id, cambio) VALUES (1, 'Venta de 2 unidades');")
    
    # Confirmamos los cambios de manera permanente en la base de datos
    conn.commit()
    print("¡Transacción confirmada con éxito (COMMIT)! Los cambios son permanentes.")

except Exception as e:
    conn.rollback()
    print("Error en Caso 1, se hizo ROLLBACK:", e)


# ==========================================
# CASO 2: El botón de Pánico (Recuperación ante errores)
# Principio ACID: Atomicidad frente al error humano
# ==========================================
print("\n--- CASO 2: El botón de Pánico (Simulación de error) ---")

# Iniciamos una nueva transacción
cursor.execute("BEGIN TRANSACTION;")
try:
    # Simulamos un error grave: DELETE masivo de productos SIN cláusula WHERE por descuido
    print("¡Simulando borrado accidental de todos los productos (sin WHERE)...!")
    cursor.execute("DELETE FROM productos;")
    
    # Si consultamos aquí dentro, parecerá que la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM productos;")
    print("Registros dentro de la transacción activa:", cursor.fetchone()[0])
    
    # ¡Detectamos el error antes de confirmar! Ejecutamos ROLLBACK para salvar los datos
    print("¡Error detectado a tiempo! Ejecutando ROLLBACK de emergencia...")
    conn.rollback()
    print("¡ROLLBACK ejecutado con éxito! Los datos fueron rescatados.")

except Exception as e:
    conn.rollback()

# Demostración de que los datos siguen intactos gracias al ROLLBACK
cursor.execute("SELECT * FROM productos;")
print("Estado de productos después del ROLLBACK:", cursor.fetchall())


# ==========================================
# CASO 3: Atomicidad ante fallos lógicos
# Principio ACID: Atomicidad (Todo o nada)
# ==========================================
print("\n--- CASO 3: Atomicidad ante fallos lógicos ---")

cursor.execute("BEGIN TRANSACTION;")
try:
    # Primer paso válido: Descontar stock del producto 2 (Mouse)
    cursor.execute("UPDATE productos SET stock = stock - 5 WHERE id = 2;")
    print("Paso 1 completado: Stock de Mouse reducido temporalmente.")

    # Segundo paso que fuerza un fallo lógico (por ejemplo, intentando consultar una tabla que no existe)
    print("Ejecutando paso 2 con fallo forzado...")
    cursor.execute("INSERT INTO tabla_inexistente VALUES (999);")

    # Si todo saliera bien, haríamos commit:
    conn.commit()

except Exception as e:
    print(f"¡Fallo detectado en la operación: {e}")
    print("La atomicidad obliga a que, si algo falla, NADA se guarde.")
    print("Ejecutando ROLLBACK para deshacer el Paso 1...")
    conn.rollback()
    print("¡Rollback aplicado! El stock del Mouse se restauró a su estado original.")

# Validación final del estado de la base de datos
print("\n--- ESTADO FINAL DE LA BASE DE DATOS ---")
cursor.execute("SELECT * FROM productos;")
print("Productos:", cursor.fetchall())
cursor.execute("SELECT * FROM ventas_log;")
print("Log de auditoría:", cursor.fetchall())

# Cerramos la conexión de forma segura
conn.close()