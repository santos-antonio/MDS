# Guia de construção dos notebooks de ESM

Este guia descreve **o que é necessário** para construir os três notebooks da aula de Escalonamento Multidimensional (ESM): bibliotecas, dados e o passo a passo de cada código.

## 1. Visão geral

| Notebook | Dados | Entrada do ESM | Ideia principal |
|---|---|---|---|
| `exemplo3_esm_distancias_geograficas.ipynb` | `atlas_dist.csv` (18 cidades) | Matriz de distâncias **já pronta** (km) | Recuperar posições a partir de distâncias; distâncias **não euclidianas** (autovalores negativos) |
| `esm_banco_mundial_2019.ipynb` | `bancomundial_2019.csv` (155 países × 8 indicadores) | Distâncias euclidianas calculadas sobre variáveis padronizadas | ESM × ACP, grupos por nível de renda |
| `esm_oms_2019.ipynb` | `oms_2019.csv` (182 países × 7 indicadores) | Idem | ESM × ACP, grupos por região da OMS |

Os dois últimos notebooks seguem a estrutura dos Exemplos 1 (Iris) e 4 (USArrests) do PDF da aula.

## 2. Ambiente e bibliotecas

### 2.1 Bibliotecas

| Biblioteca | Para que serve nos notebooks | Usada em |
|---|---|---|
| `numpy` | Álgebra matricial: matriz `H`, `B`, decomposição espectral (`np.linalg.eigh`), distâncias | Todos |
| `pandas` | Leitura do CSV, tabelas, estatísticas, agrupamentos | Todos |
| `matplotlib` | Gráficos 2D e 3D (dispersão, barras, boxplot, histograma) | Todos |
| `scipy.stats` | Assimetria, curtose e QQ-plots (`probplot`) | Banco Mundial e OMS |
| `itertools` (padrão) | `combinations`, para testar a desigualdade triangular | Exemplo 3 |
| `os`, `json`, `urllib` (padrão) | Verificar arquivo local e consultar as APIs | Banco Mundial e OMS |
| `google.colab.files` | Enviar o CSV ao Colab (só é chamada se o arquivo não existir) | Todos |

Instalação (local):

```bash
pip install numpy pandas matplotlib scipy
```

No **Google Colab** todas já vêm instaladas. No **VS Code**, instale também a extensão *Jupyter* e escolha um kernel Python.

> Não é necessário `scikit-learn`. De propósito, o ESM clássico é implementado "à mão" com `numpy`, para coincidir com a função `cmdscale()` do R usada nos slides. A classe `sklearn.manifold.MDS` usa outro algoritmo (SMACOF, minimização de *stress*) e **não** reproduziria os números do PDF.

### 2.2 Arquivos de dados

Coloque os CSV na mesma pasta dos notebooks:

| Arquivo | Origem |
|---|---|
| `atlas_dist.csv` | Página do curso (Atlas: dist). Só o triângulo inferior da matriz |
| `bancomundial_2019.csv` | World Bank Open Data (API pública), ano 2019 |
| `oms_2019.csv` | OMS, Global Health Observatory (API pública), ano 2019 |

Os notebooks do Banco Mundial e da OMS baixam os dados pela API quando o CSV não está na pasta. Se a API falhar, pedem o envio do arquivo (Colab).

## 3. Pipeline geral

Os três notebooks seguem a mesma sequência. A diferença é de onde vem a matriz `D`.

1. **Dados brutos:** CSV ou API.
2. **Limpeza:** manter só casos completos; simetrizar a matriz (Exemplo 3).
3. **Transformação:** logaritmo das variáveis assimétricas (Banco Mundial e OMS).
4. **Padronização:** `Z = (X − média) / desvio-padrão`.
5. **Matriz de distâncias `D`:** dada (Exemplo 3) ou euclidiana sobre `Z`.
6. **ESM clássico:** `D*` → `B = −½·H·D*·H` → autovalores e autovetores → `Y = Q·Λ^½`.
7. **Avaliação:** `distor`, *stress* de Kruskal, autovalores.
8. **Visualização:** gráficos 2D (`q=2`) e 3D (`q=3`).
9. **Interpretação:** configuração dos pontos, grupos, comparação com a ACP.

O diagrama visual deste pipeline está em `pipeline_esm.html`.

## 4. Passo a passo comum: o ESM clássico

Este bloco é idêntico nos três notebooks (slides 7–15).

```python
import numpy as np

def esm_classico(D):
    n = D.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n      # matriz de centralização
    B = -0.5 * H @ (D ** 2) @ H              # dupla centralização
    lam, Q = np.linalg.eigh(B)               # B é simétrica
    o = np.argsort(lam)[::-1]                # ordem decrescente
    return lam[o], Q[:, o]

lam, Q = esm_classico(D)
Y = Q[:, :q] * np.sqrt(lam[:q])              # coordenadas em R^q
distor = np.abs(lam[:q]).sum() / np.abs(lam).sum()
```

Pontos de atenção:
- `np.linalg.eigh` devolve os autovalores em ordem **crescente**; é preciso inverter.
- Se houver autovalores **negativos** (Exemplo 3), `sqrt` só deve ser aplicado aos `q` maiores, que são positivos.
- O sinal de cada autovetor é arbitrário: o gráfico pode sair espelhado em relação aos slides.

## 5. Notebook 1: distâncias geográficas (Exemplo 3)

1. **Ler** `atlas_dist.csv` com `pd.read_csv(..., index_col=0)`.
2. **Montar a matriz 18×18:** o arquivo tem só o triângulo inferior. Reindexar linhas e colunas pelas mesmas 18 cidades, trocar `NaN` por 0, somar a transposta e zerar a diagonal.
3. **Verificar** diagonal nula, simetria e valores ≥ 0.
4. **Mostrar que a Terra não é euclidiana:** Beijing, Cape Town e Rio de Janeiro; Pitágoras falha (300.155.625 ≠ 204.530.434) e a desigualdade triangular vale. Testar as 816 trincas com `itertools.combinations`. A única violação (1 km) vem do arredondamento.
5. **ESM clássico** (bloco da seção 4) e tabela de autovalores (8 de 18 são negativos).
6. **Medidas de distorção:** `distor`, Mardia (`P`) e *stress* de Kruskal.
7. **Gráficos:** mapa 2D com rótulos, gráfico 3D, distâncias originais × reconstruídas.
8. **Conferir** com os slides: `distor(q=2) = 0,6017` e `distor(q=3) = 0,7955`.

## 6. Notebooks 2 e 3: Banco Mundial e OMS

Os dois têm a mesma estrutura; só mudam as variáveis, a fonte e o rótulo dos grupos.

1. **Obter os dados**
   - Se o CSV existir, lê-lo; senão, chamar a função de download (API) e salvar o CSV.
   - Manter somente países com **todos** os indicadores (`dropna`).
   - O rótulo de grupo (renda ou região da OMS) **não entra** no cálculo; serve só para colorir os gráficos.
2. **Análise descritiva** (como nos slides 33–40)
   - Média, variância, DP, CV, mínimo, mediana, máximo, assimetria, curtose.
   - Boxplots, histogramas, QQ-plots, matriz de dispersão e matriz de correlações.
3. **Transformar** as variáveis muito assimétricas com logaritmo (PIB per capita; mortalidade infantil e materna; suicídio, com `log1p` por causa de um valor zero).
4. **Padronizar:** `Z = (X − X.mean()) / X.std()`. Sem isso, variáveis de escala grande dominariam as distâncias.
5. **ACP** pela matriz de correlações (`np.linalg.eigh(X.corr())`): autovalores, PVE e PVEA, coeficientes, correlações componente–variável, gráfico CP1 × CP2 e biplot.
6. **Distâncias euclidianas:** `D = dist_euclid(Z)`.
7. **ESM clássico** (seção 4), com `q = 2` e `q = 3`; `distor` e *stress*.
8. **Gráficos:** dispersão 2D colorida por grupo (com os países de destaque rotulados) e 3D.
9. **ESM × ACP:** conferir que `distor` coincide com a PVEA e que as coordenadas do ESM são os escores da ACP (a menos do sinal). É o mesmo fenômeno do Exemplo 4 do PDF (0,8675 = 86,75%).

Resultados de referência:

| Notebook | distor (q=2) | distor (q=3) |
|---|---|---|
| Exemplo 3 (cidades) | 0,6017 | 0,7955 |
| Banco Mundial | 0,5994 | 0,7222 |
| OMS | 0,6779 | 0,8441 |

## 7. Como executar

**VS Code:** abrir a pasta, abrir o `.ipynb`, escolher o kernel Python e executar as células em ordem (*Run All*).

**Google Colab:**
1. Enviar o `.ipynb` (*File → Upload notebook*).
2. Executar a primeira célula de dados: ela abre o seletor de arquivos; enviar o CSV correspondente.
3. Executar o restante em ordem.

## 8. Correspondência com os slides

| Tema | Slides do PDF |
|---|---|
| Matriz de dissimilaridade, propriedades, desigualdade triangular | 6–7 |
| Dupla centralização `B = −½·H·D*·H` | 8–12 |
| Decomposição espectral, Eckart–Young–Mirsky, `Y = QΛ^½` | 13–15 |
| Medidas de distorção (Kruskal, Gower, Mardia) | 16–17 |
| Exemplo 3 (cidades), `cmdscale` | 18–28 |
| Exemplos 1 e 4 (grupos, ACP × ESM) | 29–60 |
| ESM não métrico (`isoMDS`, `sammon`, `Shepard`) | 61 |
