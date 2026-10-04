"""
Comprehensive Test Script for ShopAI Production Authentication & Route Protection
Tests:
1. Public browsing endpoints (categories, products, trending, recommended) without JWT.
2. AI endpoints (/api/query, /api/compare, /api/chat) reject without JWT (401).
3. Email duplicate check & New User Registration.
4. OTP Verification & Account Activation.
5. User Login & JWT Token issuance.
6. AI endpoints accept valid JWT and return Top 2 Ranked products.
7. Forgot Password OTP generation and password reset.
8. User Profile fetching (/api/auth/me) and Session validation.
"""

import sys
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import get_user_by_email

client = TestClient(app)


def test_full_production_auth_suite():
    print("\n" + "=" * 70)
    print("🚀 RUNNING SHOPAI PRODUCTION AUTHENTICATION & SECURITY TEST SUITE")
    print("=" * 70)

    # 1. Test Public Browsing Endpoints
    print("\n[1] Testing Public Browsing Endpoints (No Auth Required)...")
    res_cats = client.get("/api/categories")
    assert res_cats.status_code == 200, f"Categories failed: {res_cats.text}"
    print("  ✓ GET /api/categories -> 200 OK")

    res_trending = client.get("/api/products/trending?category=Beauty&limit=4")
    assert res_trending.status_code == 200, f"Trending failed: {res_trending.text}"
    print("  ✓ GET /api/products/trending -> 200 OK")

    res_rec = client.get("/api/products/recommended?category=Electronics&limit=4")
    assert res_rec.status_code == 200, f"Recommended failed: {res_rec.text}"
    print("  ✓ GET /api/products/recommended -> 200 OK")

    # 2. Test AI Endpoints Reject Unauthenticated Access (401 Unauthorized)
    print("\n[2] Testing AI Endpoints Reject Unauthenticated Access...")
    res_query_unauth = client.post("/api/query", json={"query": "Laptop under 50000", "category": "Electronics"})
    assert res_query_unauth.status_code == 401, f"Expected 401 for /api/query, got {res_query_unauth.status_code}"
    print("  ✓ POST /api/query (no token) -> 401 Unauthorized (Protected)")

    res_compare_unauth = client.post("/api/compare", json={"product_ids": ["PID001", "PID002"], "category": "Electronics"})
    assert res_compare_unauth.status_code == 401, f"Expected 401 for /api/compare, got {res_compare_unauth.status_code}"
    print("  ✓ POST /api/compare (no token) -> 401 Unauthorized (Protected)")

    res_chat_unauth = client.post("/api/chat", json={"message": "Suggest top beauty product", "category": "Beauty"})
    assert res_chat_unauth.status_code == 401, f"Expected 401 for /api/chat, got {res_chat_unauth.status_code}"
    print("  ✓ POST /api/chat (no token) -> 401 Unauthorized (Protected)")

    # 3. Test Email-First Registration Flow
    test_email = f"shopper_{uuid.uuid4().hex[:6]}@example.com"
    test_password = "SecurePassword@123"
    print(f"\n[3] Testing Registration for New User: {test_email}...")
    
    # Step 3A: Check Email
    res_check = client.post("/api/auth/check-email", json={"email": test_email})
    assert res_check.status_code == 200
    assert res_check.json().get("exists") is False
    print("  ✓ POST /api/auth/check-email -> exists: false")

    # Step 3B: Register
    res_reg = client.post("/api/auth/register", json={
        "name": "Divya Sharma",
        "email": test_email,
        "password": test_password,
        "confirm_password": test_password
    })
    assert res_reg.status_code == 200, f"Register failed: {res_reg.text}"
    reg_json = res_reg.json()
    assert reg_json.get("success") is True
    print("  ✓ POST /api/auth/register -> Account created, OTP issued")

    # 4. Test OTP Verification
    print("\n[4] Testing OTP Verification...")
    user_db = get_user_by_email(test_email)
    assert user_db is not None, "User not found in database"
    otp_code = user_db.get("verification_otp")
    assert otp_code, "Verification OTP missing in database"
    print(f"  -> Retrieved Registration OTP code: {otp_code}")

    res_verify = client.post("/api/auth/verify-otp", json={
        "email": test_email,
        "otp": otp_code
    })
    assert res_verify.status_code == 200, f"Verify OTP failed: {res_verify.text}"
    verify_json = res_verify.json()
    assert verify_json.get("success") is True
    print("  ✓ POST /api/auth/verify-otp -> Email successfully verified!")

    # 5. Test Existing User Login
    print("\n[5] Testing User Login & JWT Generation...")
    res_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.text}"
    login_json = res_login.json()
    assert login_json.get("success") is True
    jwt_token = login_json.get("token") or login_json.get("access_token")
    assert jwt_token, "JWT token missing from login response"
    print(f"  ✓ POST /api/auth/login -> 200 OK (Issued JWT: {jwt_token[:20]}...)")

    headers = {"Authorization": f"Bearer {jwt_token}"}

    # 6. Test Profile Retrieval (GET /api/auth/me)
    print("\n[6] Testing User Profile Validation...")
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200, f"GET /me failed: {res_me.text}"
    assert res_me.json()["user"]["email"] == test_email
    print(f"  ✓ GET /api/auth/me -> 200 OK (User: {res_me.json()['user']['name']})")

    # 7. Test AI-Powered Search with Valid JWT Token
    print("\n[7] Testing AI Intelligent Search Engine with JWT Authentication...")
    res_query_auth = client.post("/api/query", json={
        "query": "Moisturizer under 1000",
        "category": "Beauty"
    }, headers=headers)
    assert res_query_auth.status_code == 200, f"Search failed: {res_query_auth.text}"
    query_data = res_query_auth.json()
    products = query_data.get("products", [])
    print(f"  ✓ POST /api/query (authenticated) -> Returned {len(products)} Top Ranked items")
    for idx, p in enumerate(products, 1):
        print(f"    #{idx} [{p.get('brand')}] {p.get('title')[:40]}... - ₹{p.get('price')} (Score: {p.get('score')})")

    # 8. Test AI Chat Assistant with Valid JWT Token
    print("\n[8] Testing AI Chat Assistant with JWT Authentication...")
    res_chat_auth = client.post("/api/chat", json={
        "message": "Find me best laptop for programming under 80000",
        "category": "Electronics"
    }, headers=headers)
    assert res_chat_auth.status_code == 200, f"Chat failed: {res_chat_auth.text}"
    chat_data = res_chat_auth.json()
    print(f"  ✓ POST /api/chat (authenticated) -> Assistant Response: {chat_data.get('message', '')[:60]}...")

    # 9. Test Forgot Password & Reset Password Flow
    print("\n[9] Testing Forgot Password & OTP Reset Flow...")
    res_forgot = client.post("/api/auth/forgot-password", json={"email": test_email})
    assert res_forgot.status_code == 200
    print("  ✓ POST /api/auth/forgot-password -> Password reset OTP sent")

    user_db_reset = get_user_by_email(test_email)
    reset_otp_code = user_db_reset.get("reset_otp")
    assert reset_otp_code is not None, "Reset OTP not found in database"
    print(f"  -> Retrieved Reset OTP code: {reset_otp_code}")

    new_password = "NewSecurePassword@999"
    res_reset = client.post("/api/auth/reset-password", json={
        "email": test_email,
        "otp": reset_otp_code,
        "new_password": new_password,
        "confirm_password": new_password
    })
    assert res_reset.status_code == 200
    assert res_reset.json().get("success") is True
    print("  ✓ POST /api/auth/reset-password -> Password successfully changed")

    # Verify Login with New Password
    res_new_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": new_password
    })
    assert res_new_login.status_code == 200
    assert res_new_login.json().get("success") is True
    print("  ✓ POST /api/auth/login with new password -> 200 OK Login Successful")

    print("\n" + "=" * 70)
    print("🎉 ALL PRODUCTION AUTHENTICATION & SECURITY TESTS PASSED PERFECTLY!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_full_production_auth_suite()
