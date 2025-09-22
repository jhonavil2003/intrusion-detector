
import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';
import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
  RespondToAuthChallengeCommand,
} from '@aws-sdk/client-cognito-identity-provider';

import {
  createSrpSession,
  wrapInitiateAuth,
  signSrpSession,
  wrapAuthChallenge,
  createSecretHash,
} from 'cognito-srp-helper';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const REGION = process.env.AWS_REGION || 'us-east-1';
const USER_POOL_ID = process.env.COGNITO_USER_POOL_ID;
const CLIENT_ID = process.env.COGNITO_APP_CLIENT_ID;
const CLIENT_SECRET = process.env.COGNITO_APP_CLIENT_SECRET;
const FRONTEND_ORIGIN = process.env.FRONTEND_ORIGIN || 'http://localhost:4200';
const TOKEN_MODE = (process.env.TOKEN_MODE || 'json').toLowerCase();

if (!USER_POOL_ID || !CLIENT_ID) {
  console.error('Faltan COGNITO_USER_POOL_ID o COGNITO_APP_CLIENT_ID en .env');
  process.exit(1);
}

const idp = new CognitoIdentityProviderClient({ region: REGION });

app.use(cors({ origin: [FRONTEND_ORIGIN], credentials: true }));
app.use(express.json());
app.use(cookieParser());

function metaFrom(body, req) {
  return {
    ip: body.ip || '0.0.0.0',
    deviceId: body.deviceId || 'web',
    lat: String(body.lat ?? ''),
    lon: String(body.lon ?? ''),
    country: body.country || '',
  };
}

function setTokenCookies(res, tokens) {
  const domain = process.env.COOKIE_DOMAIN || 'localhost';
  const secure = String(process.env.COOKIE_SECURE || 'false').toLowerCase() === 'true';
  const sameSite = (process.env.COOKIE_SAMESITE || 'lax').toLowerCase();
  const opts = (name, maxAge) => ({ httpOnly: true, secure, sameSite, domain, path: '/', maxAge });
  res.cookie('idToken', tokens.IdToken, opts('idToken', (tokens.ExpiresIn || 3600) * 1000));
  res.cookie('accessToken', tokens.AccessToken, opts('accessToken', (tokens.ExpiresIn || 3600) * 1000));
  if (tokens.RefreshToken) res.cookie('refreshToken', tokens.RefreshToken, opts('refreshToken', 30 * 24 * 3600 * 1000));
}

/**
 * Login con SRP + Custom Auth (opción B)
 * 1) Inicia CUSTOM_AUTH pasando CHALLENGE_NAME: SRP_A (la lib inyecta SRP_A)
 * 2) Responde PASSWORD_VERIFIER
 * 3) DefineAuthChallenge decide CUSTOM_CHALLENGE o tokens
 */
app.post('/auth/login', async (req, res) => {
  const { username, password, deviceKey, ...ctx } = req.body || {};
  if (!username || !password) return res.status(400).json({ status: 'ERROR', message: 'username y password requeridos' });

  try {
    const srp = createSrpSession(username, password, USER_POOL_ID, false);
    const secretHash = CLIENT_SECRET ? createSecretHash(username, CLIENT_ID, CLIENT_SECRET) : undefined;

    const initiateInput = wrapInitiateAuth(srp, {
      ClientId: CLIENT_ID,
      AuthFlow: 'CUSTOM_AUTH',
      AuthParameters: {
        CHALLENGE_NAME: 'SRP_A',
        USERNAME: username,
        ...(secretHash ? { SECRET_HASH: secretHash } : {}),
        ...(deviceKey ? { DEVICE_KEY: deviceKey } : {}),
      },
      ClientMetadata: metaFrom(ctx, req),
    });

    const init = await idp.send(new InitiateAuthCommand(initiateInput));

    if (init.ChallengeName === 'PASSWORD_VERIFIER') {
      const signed = signSrpSession(srp, init);
      const respondInput = wrapAuthChallenge(signed, {
        ClientId: CLIENT_ID,
        ChallengeName: 'PASSWORD_VERIFIER',
        ChallengeResponses: {
          USERNAME: username,
          ...(secretHash ? { SECRET_HASH: secretHash } : {}),
          ...(deviceKey ? { DEVICE_KEY: deviceKey } : {}),
        },
        Session: init.Session,
        ClientMetadata: metaFrom(ctx, req),
      });

      const out = await idp.send(new RespondToAuthChallengeCommand(respondInput));

      if (out.ChallengeName === 'CUSTOM_CHALLENGE') {
        return res.json({ status: 'CHALLENGE', session: out.Session, username, params: out.ChallengeParameters });
      }
      if (out.ChallengeName === 'SMS_MFA') {
        const dest = out.ChallengeParameters?.CODE_DELIVERY_DESTINATION;
        return res.json({ status: 'SMS_MFA', session: out.Session, username, destination: dest });
      }
      if (out.ChallengeName === 'NEW_PASSWORD_REQUIRED') {
        return res.json({ status: 'NEW_PASSWORD_REQUIRED', session: out.Session, username, required: out.ChallengeParameters });
      }
      if (out.AuthenticationResult) {
        if (TOKEN_MODE === 'cookie') { setTokenCookies(res, out.AuthenticationResult); return res.json({ status: 'OK' }); }
        return res.json({ status: 'OK', tokens: out.AuthenticationResult });
      }
      return res.status(400).json({ status: 'UNEXPECTED', out });
    }

    if (init.ChallengeName === 'CUSTOM_CHALLENGE') {
      return res.json({ status: 'CHALLENGE', session: init.Session, username, params: init.ChallengeParameters });
    }
    if (init.ChallengeName === 'SMS_MFA') {
      const dest = init.ChallengeParameters?.CODE_DELIVERY_DESTINATION;
      return res.json({ status: 'SMS_MFA', session: init.Session, username, destination: dest });
    }
    if (init.ChallengeName === 'NEW_PASSWORD_REQUIRED') {
      return res.json({ status: 'NEW_PASSWORD_REQUIRED', session: init.Session, username, required: init.ChallengeParameters });
    }
    if (init.AuthenticationResult) {
      if (TOKEN_MODE === 'cookie') { setTokenCookies(res, init.AuthenticationResult); return res.json({ status: 'OK' }); }
      return res.json({ status: 'OK', tokens: init.AuthenticationResult });
    }

    return res.status(400).json({ status: 'UNEXPECTED_INIT', out: init });
  } catch (e) {
    console.error('login SRP error', e);
    return res.status(401).json({ status: 'ERROR', message: e.message });
  }
});

// Responder retos (CUSTOM_CHALLENGE / SMS_MFA / NEW_PASSWORD_REQUIRED)
app.post('/auth/answer', async (req, res) => {
  const { username, code, session, challengeName = 'CUSTOM_CHALLENGE', newPassword, deviceKey, ...ctx } = req.body || {};
  if (!username || !session) return res.status(400).json({ status: 'ERROR', message: 'username y session requeridos' });

  try {
    const secretHash = CLIENT_SECRET ? createSecretHash(username, CLIENT_ID, CLIENT_SECRET) : undefined;
    const responses = (() => {
      if (challengeName === 'SMS_MFA') return { USERNAME: username, SMS_MFA_CODE: code };
      if (challengeName === 'NEW_PASSWORD_REQUIRED') return { USERNAME: username, NEW_PASSWORD: newPassword };
      return { USERNAME: username, ANSWER: code };
    })();

    const out = await idp.send(new RespondToAuthChallengeCommand({
      ClientId: CLIENT_ID,
      ChallengeName: challengeName,
      ChallengeResponses: {
        ...responses,
        ...(secretHash ? { SECRET_HASH: secretHash } : {}),
        ...(deviceKey ? { DEVICE_KEY: deviceKey } : {}),
      },
      Session: session,
      ClientMetadata: metaFrom(ctx, req),
    }));

    if (out.AuthenticationResult) {
      if (TOKEN_MODE === 'cookie') { setTokenCookies(res, out.AuthenticationResult); return res.json({ status: 'OK' }); }
      return res.json({ status: 'OK', tokens: out.AuthenticationResult });
    }
    if (out.ChallengeName) {
      return res.json({ status: out.ChallengeName, session: out.Session, username, params: out.ChallengeParameters });
    }
    return res.status(400).json({ status: 'UNEXPECTED', out });
  } catch (e) {
    console.error('answer error', e);
    return res.status(401).json({ status: 'ERROR', message: e.message });
  }
});

app.get('/health', (_, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`SRP Helper Auth server on http://localhost:${PORT}`);
});
