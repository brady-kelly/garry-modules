import msal


def get_msal_token_device_flow(app: msal.PublicClientApplication, scopes: list[str]):
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise Exception("Could not initiate authentication flow.")
    print(flow["message"]) 
    token_result = app.acquire_token_by_device_flow(flow)  
    return token_result

def get_msal_token_interactive(app: msal.PublicClientApplication, scopes: list[str], username: str):
    token_result = app.acquire_token_interactive(
        scopes=scopes,
        login_hint=username
    )    
    return token_result