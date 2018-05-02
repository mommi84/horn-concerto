# Horn Concerto
📯 Knowledge Discovery in RDF Datasets using SPARQL Queries.

To install Horn Concerto, clone its repository and cd into it.

```bash
git clone https://github.com/mommi84/horn-concerto.git
cd horn-concerto
```

## Mining existing endpoints

The current algorithm works with any SPARQL endpoint. To test it, run it with:

```bash
python horn_concerto_parallel.py
```

This will start a rule-mining task on http://dbpedia.org/sparql using default parameter values. Rules will be saved in files as `OUTPUT_FOLDER/rules-*.tsv`.


## Mining data dumps

If your data is only available as RDF dump, install Virtuoso through Docker. Admin rights might be needed.

```bash
bash install-virtuoso.sh
```

After launching the Docker instance with `docker start virtuoso`, install a graph by launching:

```bash
bash install-graph.sh filename.nt http://desired.graph.name
bash install-graph.exec
```

and finally launch the mining phase with:

```bash
python horn_concerto_parallel.py http://localhost:8890/sparql http://desired.graph.name MIN_CONFIDENCE N_PROPERTIES N_TRIANGLES OUTPUT_FOLDER
```

where `MIN_CONFIDENCE` belongs to inteval [0,1] (default=0.001), `N_PROPERTIES` is the number of top properties to consider (default=100), `N_TRIANGLES` is the number of top properties closing a 3-clique (default=10).

Rules will be saved in files as `OUTPUT_FOLDER/rules-*.tsv`.

## Inference

Horn Concerto can infer new triples in the graph using the previously discovered rules.

```bash
python horn_concerto_inference.py ENDPOINT GRAPH_NAME RULES_FOLDER INFER_FUN
```

where `INFER_FUN` is the inference function which can have the following values: `A` (average), `M` (maximum), `P` (opposite product). Discovered triples and their confidence values will be found in file `inferred_triples.txt`.

## Paper

If you use Horn Concerto in your research, please cite: https://arxiv.org/abs/1802.03638

```
@proceedings{soru-hc-2018,
    author = "Tommaso Soru and Andr\'e Valdestilhas and Edgard Marx and Axel-Cyrille {Ngonga Ngomo}",
    title = "Beyond Markov Logic: Efficient Mining of Prediction Rules in Large Graphs",
    year = "2018",
    journal = "CoRR",
    url = "https://arxiv.org/abs/1802.03638",
}
```
