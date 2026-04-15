from sqlmodel import Field, SQLModel
from datetime import datetime as Date


class Processos(SQLModel, table=True):
    namekey: str = Field(nullable=False, unique=True, primary_key=True, index=True)
    n_containers: int = Field(nullable=False)
    n_freetime: int | None = Field(default=None)
    data_eta: Date | None = Field(default=None)
    numerario_fechado: bool = Field(default=False, nullable=False)
    excluido: bool = Field(default=False, nullable=False)

class Containers(SQLModel, table=True):
    namekey: str = Field(nullable=False, unique=True, primary_key=True, index=True)
    tipo_container: int = Field(nullable=False)
    codigo_container: int = Field(nullable=False)
    excluido: bool = Field(default=False, nullable=False)

class Carregamentos(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True, nullable=False, unique=True)
    processo: str | None = Field(default=None, nullable=True, foreign_key="processos.namekey", index=True)
    container: str | None = Field(default=None, nullable=True, foreign_key="containers.namekey", index=True)
    terminal: str | None = Field(default=None, nullable=True)
    transportadora: str | None = Field(default=None, nullable=True)
    status_agendamento: str | None = Field(default=None, nullable=True)
    data_devolucao: Date | None = Field(default=None, nullable=True)
    minuta_recebida: bool = Field(default=False)
    demurrage: bool | None = Field(default=None, nullable=True)
    data_inspecao: Date | None = Field(default=None, nullable=True)
    cdk_tratativa: str | None = Field(default=None, nullable=True)
    cobrancas_html: str | None = Field(default=None, nullable=True)
    cobrancas_itens: str | None = Field(default=None, nullable=True) # JSON Array (type notation: json[])
    data_solicitacao_isencao: Date | None = Field(default=None, nullable=True)
    valor_devido: float | None = Field(default=None, nullable=True)
    pagamento_realizado: bool = Field(default=False, nullable=False)
    arquivos_enviados: str = Field(nullable=False) # JSON Array (type notation: json[])
    processo_finalizado: bool = Field(default=False, nullable=False)
    excluido: bool = Field(default=False, nullable=False)

class Dados_tol(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data_refresh: Date = Field(nullable=False)
    dados_agendamento: str = Field(nullable=False) # JSON
    dados_processos: str = Field(nullable=False) # JSON