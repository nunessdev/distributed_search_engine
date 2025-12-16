# Projeto Sistemas Distribuídos 2025 - Instruções

## Aviso

Este projeto foi desenvolvido e testado em Arch Linux, pelo que as instruções podem mudar ligeiramente para outros sistemas operativos.

## Setup

Antes da execução, é necessário garantir que todos estes passos são cumpridos para o bom funcionamento dos programas. Todos estes passos têm que ser feitos em ambos os PCs/VMs para teste, se assim for o caso.

- Extrair todos os ficheiros e pastas do ficheiro ZIP para uma pasta comum.
- Garantir que as dependências do Python estão instaladas. Pessoalmente usei um virtual environment em que todas estão instaladas (são apenas usadas as packages previstas para o projeto, no entanto todas elas se encontram no ficheiro `requirements.txt`).
- Correr o script dentro da pasta `/protos` para gerar os ficheiros necessários para as comunicações RPC.
- Alterar os IPs para os pretendidos. Estes encontram-se hardcoded no início dos diferentes programas, e como default todos estão definidos para `localhost`. Mais abaixo colocarei uma lista de todas as ocorrências. As ports também se encontram hardcoded, exceto as dos barrels.
- O LLM utilizado para a análise contextualizada foi o modelo tinyllama que corre localmente, pelo que é necessária a instalação do mesmo recorrendo aos seguintes passos:
```bash
 $ curl -fsSL https://ollama.com/install.sh | sh
 
 $  ollama pull tinyllama
```
Assim, o modelo devera estar pronto a receber pedidos REST através do endpoint `localhost:11434`.

Depois de todos os passos cumpridos, os programas estarão prontos a executar.

## Execução

Tanto para o teste em apenas um PC como para dois, os passos aplicam-se da mesma forma, desde que esteja garantido que os IPs estão configurados de forma correta. Para testar, basta correr os programas pela seguinte ordem:

Barrels:
```bash
$ python storage_barrel.py <barrel_name> <port>

Exemplo:

$ python storage_barrel.py barrel1 8184

$ python storage_barrel.py barrel2 8185
```

Gateway:
```bash
$ python gateway.py
```

Downloader:
```bash
$ python downloader.py
```
Client:
```bash
$ python client.py
```
### Frontend

Para aceder à frontend basta executar o seguinte comando e aceder ao link com a port escolhida:
```bash
$ uvicorn app.main:app --reload --port 8080
```


## Ocorrências de hardcoded IPs

|      Programa       | Linha |               Função                 |
|:-------------------:|:-----:|:------------------------------------:|
|     gateway.py      |  10   |        IP Storage Barrel 1           |
|     gateway.py      |  11   |        IP Storage Barrel 2           |
|     gateway.py      |  12   |            IP Gateway                |
|  storage_barrel.py  |  166  | IP do PC/VM onde o barrel vai correr |
|    downloader.py    |  36   |            IP Gateway                |
|    downloader.py    |  37   |        IP Storage Barrel 1           |
|    downloader.py    |  38   |        IP Storage Barrel 2           |
|     client.py       |  6    |            IP Gateway                |

#### Diogo Alçada Nunes - 2020216260