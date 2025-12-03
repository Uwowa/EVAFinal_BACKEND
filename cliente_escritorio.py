import requests
import getpass
import sys

BASE_URL = 'http://127.0.0.1:8000/api/'
TOKEN = None

def login():
    global TOKEN
    print("\n--- Iniciar Sesión ---")
    username = input("Usuario: ")
    password = getpass.getpass("Contraseña: ")
    
    try:
        response = requests.post(f'{BASE_URL}token-auth/', data={'username': username, 'password': password})
        if response.status_code == 200:
            TOKEN = response.json()['token']
            print("Login exitoso!")
            return True
        else:
            print("Credenciales inválidas.")
            return False
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor. Asegúrate de que Django esté corriendo.")
        return False

def get_headers():
    return {'Authorization': f'Token {TOKEN}'}

def listar_etiquetas():
    response = requests.get(f'{BASE_URL}etiquetas/', headers=get_headers())
    if response.status_code == 200:
        etiquetas = response.json()
        print("\n--- Lista de Etiquetas ---")
        print(f"{'ID':<5} {'Nombre':<20} {'Color':<10}")
        print("-" * 35)
        for e in etiquetas:
            print(f"{e['id']:<5} {e['nombre']:<20} {e['color']:<10}")
    else:
        print("Error al obtener etiquetas.")

def crear_etiqueta():
    nombre = input("Nombre de la etiqueta: ")
    color = input("Color (Hex, ej: #FF0000): ")
    data = {'nombre': nombre, 'color': color}
    response = requests.post(f'{BASE_URL}etiquetas/', data=data, headers=get_headers())
    if response.status_code == 201:
        print("Etiqueta creada exitosamente.")
    else:
        print(f"Error: {response.text}")

def actualizar_etiqueta():
    id_etiqueta = input("ID de la etiqueta a actualizar: ")
    nombre = input("Nuevo nombre (Enter para mantener): ")
    color = input("Nuevo color (Enter para mantener): ")
    
    data = {}
    if nombre: data['nombre'] = nombre
    if color: data['color'] = color
    
    response = requests.patch(f'{BASE_URL}etiquetas/{id_etiqueta}/', data=data, headers=get_headers())
    if response.status_code == 200:
        print("Etiqueta actualizada exitosamente.")
    else:
        print(f"Error: {response.text}")

def eliminar_etiqueta():
    id_etiqueta = input("ID de la etiqueta a eliminar: ")
    response = requests.delete(f'{BASE_URL}etiquetas/{id_etiqueta}/', headers=get_headers())
    if response.status_code == 204:
        print("Etiqueta eliminada exitosamente.")
    else:
        print(f"Error: {response.text}")

def menu():
    while True:
        print("\n--- Gestión de Etiquetas (Escritorio) ---")
        print("1. Listar Etiquetas")
        print("2. Crear Etiqueta")
        print("3. Actualizar Etiqueta")
        print("4. Eliminar Etiqueta")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            listar_etiquetas()
        elif opcion == '2':
            crear_etiqueta()
        elif opcion == '3':
            actualizar_etiqueta()
        elif opcion == '4':
            eliminar_etiqueta()
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")

if __name__ == '__main__':
    if login():
        menu()
