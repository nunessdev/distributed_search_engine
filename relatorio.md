# Relatório do Trabalho Prático
### Googol: Motor de pesquisa de páginas Web

**Sistemas Distribuídos — Ano Letivo 2025/2026 — PL2**  
**Diogo Nunes — nº 2020216260**

## Introdução
Neste trabalho foi desenvolvido um motor de pesquisa capaz de indexar automáticamente páginas web e permitir pesquisas sobre o conjunto das mesmas. O projeto foi desenvolvido em Python e conta com uma arquitetura distribuída composta por vários componentes que comunicam através de RPC.

![Arquitetura](./arquitetura.png)

## Arquitetura de Software

### URL Queue
Quando comecei a desenvolver o projeto, achei que a parte por onde faria mais sentido começar seria o Downloader e a funcionalidade da URL Queue, e para isso tinha que decidir onde ela iria ficar guardada. Como os componentes que teriam interação direta com a URL Queue seriam os Downloaders e a Gateway, achei que faria sentido implementar a funcionalidade da URL Queue dentro do programa da Gateway. Assim, tanto o Client como o Downloader conseguem chamar a mesma função RPC para introduzir URLs na Queue para mais tarde serem indexados pelos Downloaders.

### Gateway
Tal como já explicado, a Gateway é responsável pela URL Queue. Para isso, tem a função `putNew()` que pode ser chamada tanto pelos Downloaders como pelos Clients. Esta função tem como objetivo inserir um novo link na URL Queue. A Gateway tem também a função RPC `takeNext()`, que é chamada pelos Downloaders quando querem um novo link da URL Queue para processar. Para além disto, a Gateway funciona também como ponte entre os Clients e todo o sistema, tendo funções RPC que permitem aos Clients efetuarem diferentes tarefas, como pesquisa. Para a pesquisa, a Gateway tem duas funções RPC muito idênticas:
- `search()`: devolve os resultados da pesquisa com base nas palavras introduzidas;
- `getIncomingLinks()`: devolve uma lista de páginas web que têm um link para o URL atualmente a ser analisado pelo Client.

### Client
O programa do Client serve de interface para um utilizador do sistema efetuar diferentes tarefas. É no Client que se encontra toda a lógica para a paginação de resultados de 10 em 10 quando estes são apresentados, fazendo uma seleção e apresentando um menu com diferentes opções antes e após a pesquisa. É através destes menus que os utilizadores podem efetuar chamadas de funções para a Gateway.

Neste projeto foram implementadas as seguintes funcionalidades:
- indexação de URLs,
- pesquisa,
- paginação dos resultados,
- apresentação do título e preview do conteúdo dos resultados,
- consulta da lista de páginas que ligam para um resultado específico.

### Downloaders
Os Downloaders são responsáveis por todo o web crawling e indexação constante de URLs. Eles começam o seu funcionamento através da função RPC `takeNew()` da Gateway, que devolve um novo link da URL Queue. Este link é então visitado e o seu conteúdo é extraído e armazenado. O texto é tokenizado (retiram-se caracteres especiais e palavras com menos de 3 letras) e enviado para todos os Storage Barrels através da função RPC `addToIndex()`, que adiciona a palavra e o respetivo link ao índice invertido. O título e parte do texto são também enviados para os Barrels como metadados através da
função `addPageMeta()`. Por fim, todos os novos links encontrados são enviados para a Gateway para serem
adicionados à URL Queue caso ainda não tenham sido visitados, sendo também enviados para os Barrels para manter o mapeamento de ligações entre páginas.

### Barrels
Os Barrels funcionam como armazenamento central do sistema, e realizam as pesquisas pedidas pela Gateway. Estão constantemente a receber dados dos Downloaders e a indexar os mesmos em diferentes estruturas de dados. Os Barrels criam ficheiros de objetos com recurso à biblioteca `pickle` para manter uma base de dados persistente em memória, evitando perda de progresso caso algum deles deixe de funcionar. Caso um Barrel seja interrompido e reiniciado, este consegue ler e importar os dados que lhe correspondem, embora não consiga sincronizar automaticamente com outros Barrels mais atualizados.

Os Barrels contam com várias funções RPC, como:
- `addToIndex()`,
- `addLinkTracking()`,
- `addPageMeta()`.  

Estas funções são chamadas pelos Downloaders para armazenar diferentes tipos de links nas suas estruturas de dados.  
Além disso, possuem as funções de pesquisa chamadas pela Gateway:
- `getIncomingLinks()`: recebe um URL e devolve todas as páginas que contêm ligações para esse endereço;  
- `search()`: devolve resultados ordenados por relevância (número de ligações recebidas), incluindo metadados como o título e uma preview do texto para o Client.

## Meta 2

### Alterações Meta 1
A alteração mais substancial feita ao código da meta 1 foi a passagem da lógica da paginação para os storage_barrel, deste modo não cairia no erro de voltar a implementar a paginação do lado do cliente também na interface gráfica.

### rpc_client.py
Este ficheiro serve de ponte entre toda a interface e a gateway. É o rpc_client que estabelece a ligação com as funções RPC da gateway.

### routes.py
Define todos os endpoints HTTP usados pela aplicação como também a arquitetura MVC que processa a lógica necessária, chama a função RPC correspondente e devolve uma resposta usando uma das templates criadas. Neste ficheiro também é definida a API REST do Ollama para gerar resumos com recurso a um LLM.

Endpoints:

GET / - Página inicial
GET /search - Página de pesquisa
POST /search - Processa pesquisa e devolve resultados
GET /index - Página de indexação
POST /index - Indexa URL introduzido
POST /links - Mostra URLs que ligam a uma página específica

### Estrutura da interface
A interface tem uma organização intuitiva. A página inicial contém duas ligações que encaminham para duas novas páginas, pesquisa ou indexação de um URL.

A página de pesquisa funciona de forma idêntica ao que estamos habituados em qualquer search engine, introduzimos os termos de pesquisa e é carregada uma nova página com os 10 resultados recebidos e toda a informação sobre quantas páginas de resultados existem ainda. Quando navegamos entre as páginas, a função RPC de pesquisa é chamada novamente para receber os novos resultados correspondentes à página atual. No topo da página, antes dos resultados de pesquisa aparecerá sempre um pequeno resumo contextualizado, gerado pelo LLM. Em cada resultado haverá um link associado que abre um novo separador com a informação de que URLs ligam para a página em questão.

A página de indexação é também muito simples, basta introduzir um link no formato correto, carregar no botão e será então chamada a função RPC de indexação da gateway que fará todo o trabalho como na meta 1.