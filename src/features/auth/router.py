import html

from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import HTMLResponse
from .schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)
from .service import AuthService, build_user_response
from .dependencies import get_current_user
from .constants import PASSWORD_RESET_EMAIL_SENT, PASSWORD_RESET_SUCCESS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **password**: 8-16 characters, including letters, numbers, special characters, and one uppercase letter
    - **full_name**: Optional user full name
    - **username**: Optional username
    """
    # Register user
    user_doc = await AuthService.register(user_data)
    
    # Create tokens
    access_token, expires_in = AuthService.create_access_token(str(user_doc["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user_doc["_id"]))
    
    # Build response
    user_response = build_user_response(user_doc)
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Login with email or username and password
    
    Returns access token and refresh token
    """
    # Authenticate user
    user = await AuthService.login(credentials.identifier, credentials.password)
    
    # Create tokens
    access_token, expires_in = AuthService.create_access_token(str(user["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user["_id"]))
    
    # Build response
    user_response = build_user_response(user)
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Returns new access token
    """
    # Verify refresh token
    payload = AuthService.verify_token(request.refresh_token, token_type="refresh")
    user_id = payload.get("sub")
    
    # Create new access token
    access_token, expires_in = AuthService.create_access_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Send a password reset link to the user's email
    """
    await AuthService.forgot_password(request.email)

    return ForgotPasswordResponse(
        message=PASSWORD_RESET_EMAIL_SENT,
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(token: str = Query(...)):
    """
    Show a reset password page for links sent by email.
    Validates password strength client-side and redirects to frontend on success.
    """
    escaped_token = html.escape(token, quote=True)
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reset password — Cardly</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: 'Inter', system-ui, sans-serif;
      background: #0b0f19;
      color: #e2e8f0;
      padding: 16px;
    }}
    .card {{
      width: 100%;
      max-width: 420px;
      background: linear-gradient(145deg, #141e2e, #0f1724);
      border: 1px solid rgba(255,255,255,0.07);
      border-radius: 20px;
      padding: 32px;
      box-shadow: 0 32px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(45,212,191,0.06);
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 28px;
    }}
    .logo-icon {{
      width: 38px; height: 38px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0d9488, #0891b2);
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 18px; color: white;
    }}
    .logo-text {{
      font-size: 18px; font-weight: 700;
      background: linear-gradient(135deg, #2dd4bf, #06b6d4);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    h1 {{ font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; }}
    .subtitle {{ font-size: 13px; color: #64748b; margin-bottom: 24px; }}
    label {{
      display: block;
      font-size: 11px; font-weight: 600;
      color: #64748b;
      text-transform: uppercase; letter-spacing: 0.1em;
      margin-bottom: 6px;
    }}
    input[type=password] {{
      width: 100%;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 11px 16px;
      font-size: 14px;
      color: #e2e8f0;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      margin-bottom: 16px;
    }}
    input[type=password]:focus {{
      border-color: rgba(45,212,191,0.4);
      box-shadow: 0 0 0 3px rgba(45,212,191,0.08);
    }}
    .hint {{
      font-size: 11px; color: #475569;
      margin-top: -12px; margin-bottom: 16px;
      line-height: 1.5;
    }}
    button {{
      width: 100%;
      padding: 12px;
      border: none; border-radius: 12px;
      background: linear-gradient(135deg, #0d9488, #0891b2);
      color: white; font-size: 14px; font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 20px rgba(13,148,136,0.25);
      transition: opacity 0.2s, transform 0.1s;
      margin-top: 4px;
    }}
    button:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    button:disabled {{ opacity: 0.4; cursor: not-allowed; transform: none; }}
    .msg {{
      margin-top: 14px;
      padding: 12px 16px;
      border-radius: 12px;
      font-size: 13px;
      display: none;
    }}
    .msg.error  {{ display: block; background: rgba(239,68,68,0.1);  border: 1px solid rgba(239,68,68,0.2);  color: #f87171; }}
    .msg.success {{ display: block; background: rgba(45,212,191,0.08); border: 1px solid rgba(45,212,191,0.2); color: #2dd4bf; }}
    .rules {{ list-style: none; margin-bottom: 16px; display: flex; flex-direction: column; gap: 4px; }}
    .rules li {{ font-size: 11px; color: #475569; display: flex; align-items: center; gap: 6px; }}
    .rules li.ok {{ color: #2dd4bf; }}
    .rules li::before {{ content: '○'; font-size: 10px; }}
    .rules li.ok::before {{ content: '●'; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <div class="logo-icon">C</div>
      <span class="logo-text">Cardly</span>
    </div>
    <h1>Reset password</h1>
    <p class="subtitle">Choose a strong new password for your account.</p>

    <form id="reset-form">
      <input type="hidden" id="token" value="{escaped_token}" />

      <label for="new-password">New password</label>
      <input id="new-password" type="password" autocomplete="new-password"
             required minlength="8" maxlength="16" placeholder="••••••••" />

      <ul class="rules" id="rules">
        <li id="r-len">8–16 characters</li>
        <li id="r-upper">At least one uppercase letter</li>
        <li id="r-num">At least one number</li>
        <li id="r-special">At least one special character</li>
      </ul>

      <label for="confirm-password">Confirm password</label>
      <input id="confirm-password" type="password" autocomplete="new-password"
             required minlength="8" maxlength="16" placeholder="••••••••" />

      <button type="submit" id="submit-btn">Reset password</button>
      <div class="msg" id="message"></div>
    </form>
  </div>

  <script>
    const pwInput  = document.getElementById('new-password');
    const rLen     = document.getElementById('r-len');
    const rUpper   = document.getElementById('r-upper');
    const rNum     = document.getElementById('r-num');
    const rSpecial = document.getElementById('r-special');

    function validate(pw) {{
      const len     = pw.length >= 8 && pw.length <= 16;
      const upper   = /[A-Z]/.test(pw);
      const num     = /[0-9]/.test(pw);
      const special = /[^A-Za-z0-9]/.test(pw);
      rLen.className     = len     ? 'ok' : '';
      rUpper.className   = upper   ? 'ok' : '';
      rNum.className     = num     ? 'ok' : '';
      rSpecial.className = special ? 'ok' : '';
      return len && upper && num && special;
    }}

    pwInput.addEventListener('input', () => validate(pwInput.value));

    const form    = document.getElementById('reset-form');
    const message = document.getElementById('message');
    const btn     = document.getElementById('submit-btn');

    form.addEventListener('submit', async (e) => {{
      e.preventDefault();
      message.className = 'msg';
      message.textContent = '';

      const token    = document.getElementById('token').value;
      const newPw    = pwInput.value;
      const confirmPw = document.getElementById('confirm-password').value;

      if (!validate(newPw)) {{
        message.className = 'msg error';
        message.textContent = 'Password does not meet the requirements above.';
        return;
      }}

      if (newPw !== confirmPw) {{
        message.className = 'msg error';
        message.textContent = 'Passwords do not match.';
        return;
      }}

      btn.disabled = true;
      btn.textContent = 'Resetting...';

      const res  = await fetch('/api/auth/reset-password', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ token, new_password: newPw }})
      }});
      const data = await res.json().catch(() => ({{}}));

      if (!res.ok) {{
        message.className = 'msg error';
        message.textContent = data.detail || 'Could not reset password.';
        btn.disabled = false;
        btn.textContent = 'Reset password';
        return;
      }}

      message.className = 'msg success';
      message.textContent = 'Password reset successfully! Redirecting to login...';
      form.reset();
      setTimeout(() => {{ window.location.href = 'http://localhost:5173'; }}, 2000);
    }});
  </script>
</body>
</html>
"""


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using a valid reset token
    """
    await AuthService.reset_password(request.token, request.new_password)

    return MessageResponse(message=PASSWORD_RESET_SUCCESS)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user profile
    
    Requires: Valid JWT access token
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout current user
    
    Note: Token should be invalidated on client side
    Server-side: Consider implementing token blacklist for production
    """
    return {"message": "Logged out successfully"}
