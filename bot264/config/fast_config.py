from flask import Flask, Request, request 
from flask_cors import CORS, cross_origin
from firebase_admin.auth import verify_id_token
app = Flask(__name__)
CORS(app, support_credentials=True)

# export async function decodeIDToken(req: Request): Promise<(UserRecord | undefined)> {
#     if (req.headers?.authorization?.startsWith('Bearer ')) {
#         const idToken = req.headers.authorization.split('Bearer ')[1];
#         try {
#             const decodedToken: DecodedIdToken = await getAuth().verifyIdToken(idToken);
#             return await getAuth().getUser(decodedToken.uid);
#         } catch (err) {
#             console.log(err);
#         }
#     }
#     return undefined;
# }

async def check_firebase_auth(r: Request):
    authorization = request.headers.get('authorization')
    if authorization is None:
        return None
    if not (authorization.startswith("Bearer ")):
        return None
    token = authorization.split("Bearer ")[1]
    try:
        return verify_id_token(token) 
    except:
        return None

@app.get("/")
def welcome():
    check_firebase_auth(request)
    return {"ping": "pong"}

@app.get("/servers")
async def get_servers():
    user = await check_firebase_auth(request)
    if not user:
        return 'not authenticated', 400
    return {
        "servers": [
            {
                "example": "example 1"
            }
        ]
    }

def flask_app():
    return app