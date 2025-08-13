from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cálculos de Transistor BJT", version="1.0")

# Permitir qualquer origem (frontend no Vercel ou celular)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Entrada(BaseModel):
    Vbb: float
    RC: float
    RB: float
    Vcc: float
    Beta: float
    Vbe: float = 0.7
    Vcesat: float = 0.2

class Saida(BaseModel):
    IC: float
    VCE: float
    Potencia: float
    regiao: str
    IB: float
    IC_max: float
    load_line_vce: List[float]
    load_line_ic: List[float]
    ponto_q: dict

@app.post("/calcular", response_model=Saida)
def calcular_dados(entrada: Entrada):
    Vbb, RC, RB, Vcc, Beta, Vbe, Vcesat = entrada.Vbb, entrada.RC, entrada.RB, entrada.Vcc, entrada.Beta, entrada.Vbe, entrada.Vcesat

    IB = max(0.0, (Vbb - Vbe) / RB)
    IC_ativa = Beta * IB
    IC_sat = max(0.0, (Vcc - Vcesat) / RC)

    if IB == 0.0:
        regiao = "Região de Corte"
        IC = 0.0
        VCE = Vcc
    elif IC_ativa > IC_sat:
        regiao = "Região de Saturação"
        IC = IC_sat
        VCE = Vcesat
    else:
        regiao = "Região Ativa"
        IC = IC_ativa
        VCE = Vcc - IC * RC

    Potencia = VCE * IC

    passos = 50
    pontos_vce = [Vcc * i / (passos - 1) for i in range(passos)]
    pontos_ic = [(Vcc - v) / RC if (Vcc - v) >= 0 else 0.0 for v in pontos_vce]
    ponto_q = {"VCE": VCE, "IC": IC}

    return {
        "IC": IC,
        "VCE": VCE,
        "Potencia": Potencia,
        "regiao": regiao,
        "IB": IB,
        "IC_max": IC_sat,
        "load_line_vce": pontos_vce,
        "load_line_ic": pontos_ic,
        "ponto_q": ponto_q
    }
