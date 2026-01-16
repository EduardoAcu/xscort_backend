#!/usr/bin/env python
"""
Script de pruebas para el flujo de forgot/reset password.
Ejecutar con: python test_forgot_password_flow.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/Users/eduardo/Documents/GitHub/xscort_backend/config')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from usuarios.models import CustomUser, PasswordResetToken
from django.utils import timezone

BASE_URL = "http://127.0.0.1:8000/api"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_forgot_password_flow():
    """Prueba el flujo completo de recuperación de contraseña"""
    
    print_header("PRUEBAS DE FLUJO: FORGOT/RESET PASSWORD")
    
    # 1. Crear usuario de prueba
    print_header("1. Preparación: Crear usuario de prueba")
    test_email = "test_forgot@example.com"
    test_username = "test_forgot_user"
    test_password = "TestPass123!"
    
    # Limpiar usuarios y tokens anteriores
    CustomUser.objects.filter(email=test_email).delete()
    CustomUser.objects.filter(username=test_username).delete()
    
    user = CustomUser.objects.create_user(
        username=test_username,
        email=test_email,
        password=test_password
    )
    print_result("Usuario creado", True, f"Email: {test_email}")
    
    # 2. Test: Solicitar recuperación con email válido
    print_header("2. POST /forgot-password/ (email válido)")
    try:
        response = requests.post(
            f"{BASE_URL}/forgot-password/",
            json={"email": test_email},
            timeout=15
        )
        success = response.status_code == 200
        print_result(
            "Solicitud de recuperación enviada",
            success,
            f"Status: {response.status_code}, Message: {response.json().get('message', 'N/A')}"
        )
        
        # Verificar que se creó un token
        token_count = PasswordResetToken.objects.filter(user=user, used=False).count()
        print_result("Token creado en BD", token_count == 1, f"Tokens activos: {token_count}")
        
    except Exception as e:
        print_result("Solicitud de recuperación", False, str(e))
        return
    
    # 3. Test: Solicitar recuperación con email que no existe (no debe revelar info)
    print_header("3. POST /forgot-password/ (email inexistente)")
    try:
        response = requests.post(
            f"{BASE_URL}/forgot-password/",
            json={"email": "noexiste@example.com"},
            timeout=5
        )
        # Debe retornar 200 sin revelar que el usuario no existe
        success = response.status_code == 200
        same_message = "Si el email existe" in response.json().get('message', '')
        print_result(
            "No revela info de usuario inexistente",
            success and same_message,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_result("Email inexistente", False, str(e))
    
    # 4. Test: Solicitud sin email
    print_header("4. POST /forgot-password/ (sin email)")
    try:
        response = requests.post(
            f"{BASE_URL}/forgot-password/",
            json={},
            timeout=5
        )
        success = response.status_code == 400
        print_result(
            "Valida email requerido",
            success,
            f"Status: {response.status_code}, Error: {response.json().get('error', 'N/A')}"
        )
    except Exception as e:
        print_result("Validación email", False, str(e))
    
    # 5. Test: Obtener token para reset
    print_header("5. Obtener token de la BD")
    try:
        reset_token = PasswordResetToken.objects.filter(user=user, used=False).first()
        if reset_token:
            token_str = reset_token.token
            print_result("Token obtenido", True, f"Token: {token_str[:20]}...")
            print_result("Token es válido", reset_token.is_valid(), 
                        f"Expira: {reset_token.expires_at}, Used: {reset_token.used}")
        else:
            print_result("Token obtenido", False, "No se encontró token")
            return
    except Exception as e:
        print_result("Obtener token", False, str(e))
        return
    
    # 6. Test: Reset password con contraseñas que no coinciden
    print_header("6. POST /reset-password/ (contraseñas no coinciden)")
    try:
        response = requests.post(
            f"{BASE_URL}/reset-password/",
            json={
                "token": token_str,
                "new_password": "NewPass123!",
                "confirm_password": "DifferentPass123!"
            },
            timeout=5
        )
        success = response.status_code == 400
        print_result(
            "Valida contraseñas coincidan",
            success,
            f"Status: {response.status_code}, Error: {response.json().get('error', 'N/A')}"
        )
    except Exception as e:
        print_result("Validación contraseñas", False, str(e))
    
    # 7. Test: Reset password con contraseña corta
    print_header("7. POST /reset-password/ (contraseña corta)")
    try:
        response = requests.post(
            f"{BASE_URL}/reset-password/",
            json={
                "token": token_str,
                "new_password": "short",
                "confirm_password": "short"
            },
            timeout=5
        )
        success = response.status_code == 400
        print_result(
            "Valida longitud mínima",
            success,
            f"Status: {response.status_code}, Error: {response.json().get('error', 'N/A')}"
        )
    except Exception as e:
        print_result("Validación longitud", False, str(e))
    
    # 8. Test: Reset password exitoso
    print_header("8. POST /reset-password/ (exitoso)")
    new_password = "NewSecurePass123!"
    try:
        response = requests.post(
            f"{BASE_URL}/reset-password/",
            json={
                "token": token_str,
                "new_password": new_password,
                "confirm_password": new_password
            },
            timeout=15
        )
        success = response.status_code == 200
        print_result(
            "Reset password exitoso",
            success,
            f"Status: {response.status_code}, Message: {response.json().get('message', 'N/A')}"
        )
        
        # Verificar que el token se marcó como usado
        reset_token.refresh_from_db()
        print_result("Token marcado como usado", reset_token.used, f"Used: {reset_token.used}")
        
    except Exception as e:
        print_result("Reset password", False, str(e))
        return
    
    # 9. Test: Intentar usar el mismo token nuevamente
    print_header("9. POST /reset-password/ (token ya usado)")
    try:
        response = requests.post(
            f"{BASE_URL}/reset-password/",
            json={
                "token": token_str,
                "new_password": "AnotherPass123!",
                "confirm_password": "AnotherPass123!"
            },
            timeout=5
        )
        success = response.status_code == 400
        print_result(
            "Token de un solo uso",
            success,
            f"Status: {response.status_code}, Error: {response.json().get('error', 'N/A')}"
        )
    except Exception as e:
        print_result("Token usado", False, str(e))
    
    # 10. Test: Login con contraseña anterior (debe fallar)
    print_header("10. POST /token/ (login con contraseña vieja)")
    try:
        response = requests.post(
            f"{BASE_URL}/token/",
            json={
                "username": test_username,
                "password": test_password  # Contraseña vieja
            },
            timeout=5
        )
        success = response.status_code == 401
        print_result(
            "Contraseña vieja no funciona",
            success,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        print_result("Login contraseña vieja", False, str(e))
    
    # 11. Test: Login con nueva contraseña
    print_header("11. POST /token/ (login con nueva contraseña)")
    try:
        response = requests.post(
            f"{BASE_URL}/token/",
            json={
                "username": test_username,
                "password": new_password  # Nueva contraseña
            },
            timeout=5
        )
        success = response.status_code == 200
        has_cookies = 'access_token' in response.cookies or 'Set-Cookie' in response.headers
        print_result(
            "Login exitoso con nueva contraseña",
            success and has_cookies,
            f"Status: {response.status_code}, Cookies: {list(response.cookies.keys())}"
        )
    except Exception as e:
        print_result("Login nueva contraseña", False, str(e))
    
    # 12. Test: Token expirado
    print_header("12. POST /reset-password/ (token expirado)")
    try:
        # Crear token expirado
        expired_token = PasswordResetToken.objects.create(
            user=user,
            token="expired_test_token_123456",
            expires_at=timezone.now() - timezone.timedelta(hours=2)
        )
        
        response = requests.post(
            f"{BASE_URL}/reset-password/",
            json={
                "token": expired_token.token,
                "new_password": "NewPass456!",
                "confirm_password": "NewPass456!"
            },
            timeout=5
        )
        success = response.status_code == 400
        print_result(
            "Token expirado rechazado",
            success,
            f"Status: {response.status_code}, Error: {response.json().get('error', 'N/A')}"
        )
        
        expired_token.delete()
    except Exception as e:
        print_result("Token expirado", False, str(e))
    
    # Limpieza
    print_header("LIMPIEZA")
    user.delete()
    print_result("Usuario de prueba eliminado", True)
    
    print_header("RESUMEN DE PRUEBAS COMPLETADO")
    print("\n✅ Todas las pruebas del flujo de forgot/reset password finalizadas.\n")

if __name__ == "__main__":
    print("\n🧪 Iniciando pruebas de flujo de forgot/reset password...")
    print("⚠️  Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000\n")
    
    try:
        test_forgot_password_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario.")
    except Exception as e:
        print(f"\n\n❌ Error crítico en las pruebas: {e}")
        import traceback
        traceback.print_exc()
