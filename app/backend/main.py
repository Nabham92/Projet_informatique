from fastapi import FastAPI
from app.backend.api.endpoints import router

app = FastAPI(title="API de Recommandation de Films", 
             description="API pour obtenir des recommandations de films personnalisées",
             version="1.0")

# Point de terminaison simple pour les vérifications de santé
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Inclure les routes de l'API sans préfixe
app.include_router(router)