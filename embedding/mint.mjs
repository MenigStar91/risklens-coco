import crypto from 'node:crypto';

// Server-only: never import this module into a client bundle.
export function keypairJwt(env, now = Math.floor(Date.now() / 1000)) {
  const key = crypto.createPrivateKey(env.SNOWFLAKE_PRIVATE_KEY.replace(/\\n/g, '\n'));
  const fingerprint = crypto.createHash('sha256')
    .update(crypto.createPublicKey(key).export({type: 'spki', format: 'der'})).digest('base64');
  const account = env.SNOWFLAKE_ACCOUNT.toUpperCase().replace(/\./g, '-');
  const user = `${account}.${env.SNOWFLAKE_USER.toUpperCase()}`;
  const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
  const body = `${encode({alg:'RS256',typ:'JWT'})}.${encode({
    iss:`${user}.SHA256:${fingerprint}`,sub:user,iat:now,exp:now+300
  })}`;
  return `${body}.${crypto.sign('RSA-SHA256',Buffer.from(body),key).toString('base64url')}`;
}

export async function mintEmbedUrl(env, fetchImpl = fetch) {
  const required = ['STREAMLIT_APP','SNOWFLAKE_ACCOUNT_URL','SNOWFLAKE_ACCOUNT','SNOWFLAKE_USER','SNOWFLAKE_ROLE','SNOWFLAKE_PRIVATE_KEY','PARENT_ORIGIN'];
  if (required.some(key => typeof env[key] !== 'string' || !env[key]))
    throw new Error('HOST_CONFIG_MISSING');
  const [db,schema,app,...extra] = env.STREAMLIT_APP.split('.');
  if (!db || !schema || !app || extra.length) throw new Error('Invalid app configuration');
  const url = new URL(env.SNOWFLAKE_ACCOUNT_URL);
  if (url.protocol !== 'https:' || !url.hostname.endsWith('.snowflakecomputing.com'))
    throw new Error('Invalid account configuration');
  url.pathname = `/api/v2/databases/${encodeURIComponent(db)}/schemas/${encodeURIComponent(schema)}/streamlits/${encodeURIComponent(app)}:generate-embed-url`;
  let jwt;
  try { jwt = keypairJwt(env); } catch { throw new Error('HOST_KEY_SIGNING_FAILED'); }
  let response;
  try { response = await fetchImpl(url, {
    method:'POST',
    headers:{'Content-Type':'application/json','Authorization':`Bearer ${jwt}`,
      'X-Snowflake-Authorization-Token-Type':'KEYPAIR_JWT','X-Snowflake-Role':env.SNOWFLAKE_ROLE},
    body:JSON.stringify({parent_origin:env.PARENT_ORIGIN}),
    signal:AbortSignal.timeout(30000),redirect:'error',cache:'no-store'
  }); } catch { throw new Error('SNOWFLAKE_NETWORK_ERROR'); }
  // Do not log Snowflake bodies or single-use URLs.
  if (!response.ok) throw new Error(`SNOWFLAKE_HTTP_${response.status}`);
  const result = await response.json();
  if (typeof result.embed_url !== 'string' || !result.embed_url.startsWith('https://'))
    throw new Error('Invalid embed response');
  return result.embed_url;
}

export async function handleEmbedRequest(request, env, authenticatedUser) {
  const headers = {'Cache-Control':'no-store, private','Content-Type':'application/json'};
  if (!authenticatedUser) return new Response(JSON.stringify({error:'Sign in to open the live demo.'}),{status:401,headers});
  if (request.method !== 'POST') return new Response(null,{status:405,headers});
  if (request.headers.get('Origin') !== env.PARENT_ORIGIN)
    return new Response(null,{status:403,headers});
  try {
    return new Response(JSON.stringify({embedUrl:await mintEmbedUrl(env)}),{headers});
  } catch (exc) {
    const allowed = /^(HOST_CONFIG_MISSING|HOST_KEY_SIGNING_FAILED|SNOWFLAKE_NETWORK_ERROR|SNOWFLAKE_HTTP_\d{3})$/;
    const code = allowed.test(exc?.message) ? exc.message : 'EMBED_RESPONSE_INVALID';
    // Log only a classified code, never a credential, upstream body or embed URL.
    console.error('RiskLens embed failure', {code});
    return new Response(JSON.stringify({error:`The live demo could not start (${code}). Please share this code.`}),{status:502,headers});
  }
}
