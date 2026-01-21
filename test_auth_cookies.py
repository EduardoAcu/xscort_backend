#!/usr/bin/env python
"""
Script de pruebas para verificar el sistema de autenticación con cookies HttpOnly.

Prueba:
1. Registro de usuario
2. Login con cookies HttpOnly
3. Acceso a endpoint protegido usando cookies
4. Logout
"""

import requests
import sys

# Configuración
BASE_URL = "http://localhost:8000"
session = requests.Session()  # Mantiene las cookies automáticamente

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_register():
    """Prueba el registro de un nuevo usuario con cookies HttpOnly"""
    print_section("TEST 1: Registro de Usuario con Cookies HttpOnly")
    
    # Limpiar cookies de sesiones anteriores
    session.cookies.clear()
    
    # Usar un usuario único para cada test
    import time
    timestamp = int(time.time())
    
    data = {
        "username": f"test_cookies_{timestamp}",
        "email": f"test_cookies_{timestamp}@example.com",
        "password": "TestPassword123!",
        "password2": "TestPassword123!",
        "fecha_nacimiento": "1990-01-01"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/register/", json=data)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        if response.status_code == 201:
            # Verificar que NO hay tokens en el JSON
            response_data = response.json()
            has_tokens_in_json = 'tokens' in response_data
            
            if has_tokens_in_json:
                print_error("⚠️  PROBLEMA: Tokens todavía presentes en JSON (no seguro)")
                print_info(f"  Response contiene 'tokens': {response_data.get('tokens', {}).keys()}")
            else:
                print_success("✨ Tokens NO expuestos en JSON (seguro)")
            
            # Verificar cookies
            print_info("\nCookies establecidas en registro:")
            has_access = 'access_token' in session.cookies
            has_refresh = 'refresh_token' in session.cookies
            
            for cookie in session.cookies:
                print(f"  - {cookie.name}: {cookie.value[:20]}... (httponly={cookie.has_nonstandard_attr('HttpOnly')})")
            
            if has_access and has_refresh and not has_tokens_in_json:
                print_success("Usuario registrado con cookies HttpOnly correctamente")
                return True
            else:
                print_error("Registro incompleto:")
                print_info(f"  - access_token cookie: {has_access}")
                print_info(f"  - refresh_token cookie: {has_refresh}")
                print_info(f"  - tokens en JSON: {has_tokens_in_json}")
                return False
        else:
            print_error(f"Error en registro: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Excepción durante registro: {e}")
        return False

def test_login():
    """Prueba el login con cookies HttpOnly"""
    print_section("TEST 2: Login con Cookies HttpOnly")
    
    # Limpiar cookies del registro para probar login desde cero
    session.cookies.clear()
    
    # Primero crear un usuario conocido para el login
    import time
    timestamp = int(time.time())
    username = f"login_test_{timestamp}"
    
    # Registrar usuario
    register_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPassword123!",
        "password2": "TestPassword123!",
        "fecha_nacimiento": "1990-01-01"
    }
    session.post(f"{BASE_URL}/api/register/", json=register_data)
    
    # Limpiar cookies del registro
    session.cookies.clear()
    
    # Ahora hacer login
    data = {
        "username": username,
        "password": "TestPassword123!"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/token/", json=data)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        # Verificar cookies
        print_info("\nCookies recibidas:")
        for cookie in session.cookies:
            print(f"  - {cookie.name}: {cookie.value[:20]}... (httponly={cookie.has_nonstandard_attr('HttpOnly')})")
        
        if response.status_code == 200:
            # Verificar que se establecieron las cookies
            has_access = 'access_token' in session.cookies
            has_refresh = 'refresh_token' in session.cookies
            
            if has_access and has_refresh:
                print_success("Login exitoso con cookies HttpOnly establecidas")
                return True
            else:
                print_error("Login exitoso pero cookies no establecidas correctamente")
                print_info(f"  - access_token: {has_access}")
                print_info(f"  - refresh_token: {has_refresh}")
                return False
        else:
            print_error(f"Error en login: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Excepción durante login: {e}")
        return False

def test_protected_endpoint():
    """Prueba acceso a endpoint protegido usando cookies"""
    print_section("TEST 3: Acceso a Endpoint Protegido")
    
    try:
        # Intentar acceder a endpoint protegido
        # Las cookies se envían automáticamente
        response = session.get(f"{BASE_URL}/api/verification/status/")
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print_success("Acceso a endpoint protegido exitoso usando cookies")
            print_info("Las cookies HttpOnly funcionan correctamente ✨")
            return True
        else:
            print_error(f"Error accediendo a endpoint protegido: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Excepción durante acceso a endpoint: {e}")
        return False

def test_logout():
    """Prueba el logout y limpieza de cookies"""
    print_section("TEST 4: Logout")
    
    try:
        response = session.post(f"{BASE_URL}/api/logout/")
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        # Verificar que las cookies fueron eliminadas
        print_info("\nCookies después del logout:")
        cookies_after = list(session.cookies)
        
        if not cookies_after:
            print_success("Logout exitoso - Cookies eliminadas")
            return True
        else:
            print_error("Cookies todavía presentes después del logout")
            for cookie in cookies_after:
                print_info(f"  - {cookie.name}")
            return False
            
    except Exception as e:
        print_error(f"Excepción durante logout: {e}")
        return False

def test_access_after_logout():
    """Prueba que no se puede acceder después del logout"""
    print_section("TEST 5: Verificar No Acceso Post-Logout")
    
    try:
        response = session.get(f"{BASE_URL}/api/verification/status/")
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Correctamente denegado el acceso después del logout")
            return True
        else:
            print_error("PROBLEMA: Todavía se puede acceder después del logout")
            return False
            
    except Exception as e:
        print_error(f"Excepción durante verificación post-logout: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "🔐 " * 20)
    print("PRUEBAS DE AUTENTICACIÓN CON COOKIES HTTPONLY")
    print("🔐 " * 20)
    
    results = {
        "Registro": test_register(),
        "Login": test_login(),
        "Endpoint Protegido": test_protected_endpoint(),
        "Logout": test_logout(),
        "Post-Logout": test_access_after_logout()
    }
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Resultado: {passed}/{total} pruebas pasadas")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema funciona correctamente.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs arriba.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error crítico: {e}")
        sys.exit(1)
