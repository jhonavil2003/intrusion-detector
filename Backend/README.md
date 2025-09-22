
# Cognito SRP Backend (cognito-srp-helper)

Este backend usa **cognito-srp-helper** para manejar SRP con Cognito sin implementar criptografía manual.

## Requisitos
- App client con `ALLOW_CUSTOM_AUTH`, `ALLOW_USER_SRP_AUTH`, `ALLOW_REFRESH_TOKEN_AUTH`.
- Triggers (opción B): `DefineAuthChallenge`, `CreateAuthChallenge`, `VerifyAuthChallengeResponse`.
- (Opcional) Client secret → define `COGNITO_APP_CLIENT_SECRET` en `.env`.

## Uso
```bash
cp .env.example .env
# Edita: AWS_REGION, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID, FRONTEND_ORIGIN
npm i
npm run dev   # API :3001, debug :9229
```

## Endpoints
- `POST /auth/login` { username, password, deviceKey? }  
- `POST /auth/answer` { username, session, challengeName, code? | newPassword? }

## Notas
- Para forzar **CUSTOM_CHALLENGE** y no `SMS_MFA`, desactiva MFA nativo en pool/usuario.
- Si tu App client tiene secreto, el backend calcula `SECRET_HASH` automáticamente.
