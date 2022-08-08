from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from ..repository import schemas, database, models
from ..security.hashing import Hash
from ..security import token
import oic
from oic.oic.message import ProviderConfigurationResponse
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import RegistrationResponse
from oic import rndstr
from oic.utils.http_util import Redirect
from oic.oic.message import ClaimsRequest, Claims
import warnings
import contextlib
from oic.oic.message import AuthorizationResponse

import requests
from urllib3.exceptions import InsecureRequestWarning
from fastapi.responses import RedirectResponse
import time
import os
router = APIRouter(tags=['Authentication'])
inner_state = rndstr()
nonce = rndstr()
client = Client(client_authn_method=CLIENT_AUTHN_METHOD)


@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    old_merge_environment_settings = requests.Session.merge_environment_settings

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

def get_login_url():
    # Informações padrões sobre os end-points do Provedor OpenID (OP - WSO2 IS)
    WS02_ISSUER = os.getenv('WS02_ISSUER')
    info_issuer = {}

    with no_ssl_verification(): 
        info_issuer = requests.get("{}/oauth2/oidcdiscovery/.well-known/openid-configuration".format (WS02_ISSUER)).json()

    op_info = ProviderConfigurationResponse( 
        version ="1.0", 
        issuer = info_issuer["issuer"],
        authorization_endpoint = info_issuer["authorization_endpoint"],
        token_endpoint = info_issuer["token_endpoint"],
        jwks_uri = info_issuer["jwks_uri"],
        userinfo_endpoint = info_issuer["userinfo_endpoint"],
        revocation_endpoint = info_issuer["revocation_endpoint"],
        introspection_endpoint= info_issuer["introspection_endpoint"],
        end_session_endpoint = info_issuer["end_session_endpoint"],
        srv_discovery_url = "{}/oauth2/oidcdiscovery/.well-known/openid-configuration".format (WS02_ISSUER),
        #discovery_endpoint = info_issuer["discovery_endpoint"],
    )

    client.handle_provider_config(op_info, op_info['issuer'])

    info = {
        "client_id": os.getenv('WS02_CLIENT_ID'), 
        "client_secret": os.getenv('WS02_CLIENT_SECRET')
    }

    client_reg = RegistrationResponse(**info)

    client.store_registration_info(client_reg)

    args = {
        "enabled": True,
        "authority": "{}/oauth2/oidcdiscovery/".format (WS02_ISSUER),
        "post_logout_redirect_uri": "{}/login/0".format (os.getenv ('URL_FRONTEND')),
        "client_id": client.client_id,
        "response_type": ['code'], # Determina o fluxo de autorização OAuth 2.0 que será utilizado
        "scope": ["openid profile email"], #Por padrão é inserido 'openid', mas também pode ser inserido informações a qual deseja ter do usuário, como exemplo, email.
        "nonce": nonce, #É um valor de string usado para associar uma sessão de cliente a um token de ID e para mitigar ataques de repetição
        "redirect_uri": ['{}/logincallback'.format (os.getenv ('URL_BACKEND'))], #URL que o Provedor OpenID deve retornar após autenticação ser realizada
        "state": inner_state, #É utilizado para controlar as respostas às solicitações pendentes
    
    }

    auth_req = client.construct_AuthorizationRequest(request_args=args)
    return auth_req.request(client.authorization_endpoint)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db=Depends(database.get_db)):

    user = db.users.find_one({'email': request.username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user['password'], request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = token.create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer", "user": schemas.User(**user)}

@router.get('/logintoken')
def login(tk:str, db=Depends(database.get_db)):
    print(tk)

    user = db.users.find_one({'email': Hash.decrypt_message(tk)})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")

    access_token = token.create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer", "user": schemas.User(**user)}

@router.get('/authws02')
def ws02(db=Depends(database.get_db)):
    return RedirectResponse (get_login_url())
    
@router.get('/logoutcallback')
def logout():
    return RedirectResponse (client.end_session_endpoint)

#Rota que trata informações retornadas pela provedor OpenID (OP - WSO2 IS)
@router.get('/logincallback')
def callback(request: Request, db=Depends(database.get_db)):
    params = request.query_params
    
    aresp = client.parse_response(AuthorizationResponse, info=str(params), sformat="urlencoded")

    assert inner_state == aresp['state']   #Verifica se o state enviado na solicitação de autenticação é o mesmo retornado pelo Provedor Open ID (OP - WSO2 IS)

    with no_ssl_verification():        
        # Utiliza o Code Grant Type retornado pelo OP para solicitar ao OP o Access Token e ID Token
        args = {"code": aresp['code']}
        resp = client.do_access_token_request(state=aresp['state'], 
                                            request_args=args, 
                                            authn_method="client_secret_basic")

    if(resp["access_token"]!= ""):
        with no_ssl_verification():
            userinfo = client.do_user_info_request(access_token=resp["access_token"], scope='profile')
            userinfo['email'] = userinfo['email'] if 'email' in userinfo else userinfo['sub']
            userinfo['given_name'] = userinfo['given_name'] if 'given_name' in userinfo else userinfo['sub']

            print(userinfo)
            user = db.users.find_one({'email': userinfo['email']})
            if user:
                return RedirectResponse ('%s/login/%s' % (os.getenv('URL_FRONTEND'), Hash.encrypt_message(userinfo['email'])))
            
            new_user = schemas.User(
                name=userinfo['given_name'], 
                email=userinfo['email'], 
                password=Hash.bcrypt(aresp['state']),
                ws02token=resp)
            
            if hasattr(new_user, 'id'):
                delattr(new_user, 'id')

            new_user = db.users.insert_one(new_user.dict(by_alias=True))

            return RedirectResponse ('%s/login/%s' % (os.getenv('URL_FRONTEND'), Hash.encrypt_message(userinfo['email'])))
    
    else:
        return "ERRO DE AUTENTICAÇÃO"
