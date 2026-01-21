#!/usr/bin/env python
"""
Script para diagnosticar problemas con cookies HttpOnly
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("DIAGNÓSTICO DE COOKIES")
print("="*60)

# 1. Test login
print("\n1. Probando login...")
session = requests.Session()  # Usar sesión para mantener cookies

try:
    response = session.post(
        f"{BASE_URL}/api/token/",
        json={"username": "testuser", "password": "testpass123"},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"\nCookies recibidas:")
    for cookie in session.cookies:
        print(f"  - {cookie.name}: {cookie.value[:20]}...")
        print(f"    Domain: {cookie.domain}")
        print(f"    Path: {cookie.path}")
        print(f"    Secure: {cookie.secure}")
        print(f"    HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
    
    print(f"\nHeaders Set-Cookie:")
    if 'Set-Cookie' in response.headers:
        print(f"  {response.headers['Set-Cookie']}")
    else:
        print("  (No Set-Cookie header)")
    
    # 2. Test endpoint autenticado
    print("\n2. Probando endpoint autenticado...")
    response2 = session.get(
        f"{BASE_URL}/api/profiles/mi-perfil/",
        timeout=10
    )
    
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        print("✅ Cookies funcionando correctamente")
        print(f"Response: {response2.json()}")
    else:
        print("❌ Cookies NO funcionan")
        print(f"Error: {response2.json()}")
    
    # 3. Verificar cookies enviadas
    print(f"\nCookies enviadas en la segunda request:")
    for cookie in session.cookies:
        print(f"  - {cookie.name}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
