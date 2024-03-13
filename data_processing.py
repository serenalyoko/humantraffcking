import pandas as pd
import openpyxl
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import netwulf as nw

def process_number(num):
    new = ""
    num = str(num)
    for i in range(len(num)):
        char = num[i]
        if char == "(" or char == ")" or char == "-" or char == " ":
            continue
        else:
            new = new + char
    return new

def extract_domain(url):
    domain = ""
    count = 0
    for i in range(len(url)):
        char = url[i]
        if count < 3:
            domain += char
        if char == "/":
            count += 1
    return domain


if __name__ == "__main__":
    xls = pd.ExcelFile('job-listing-in-fringe-media.xlsx')
    raw = pd.read_excel(xls, 'Sheet4')
    numbers = raw["number"]
    domains = raw["domain"]
    raw_labels = raw["Label"]
    node_list = {"id":[], "label":[]}


    new_numbers = []
    for i in range(len(numbers)):
        new_numbers.append(process_number(numbers[i]))

    new_domains = []
    labels = {}
    for i in range(len(domains)):
        processed = extract_domain(domains[i])
        labels[processed] = raw_labels[i]
        new_domains.append(processed)

    for n in new_numbers:
        labels[str(n)] =  "number"

    edge_list = {"source":[], "target":[]}
    for i in range(len(new_domains)):
        edge_list["source"].append(new_numbers[i])
        edge_list["target"].append(new_domains[i])


    for n in labels:
        node_list["id"].append(n[0])
        node_list["label"].append(n[1])

    """
    escort = []
    forum = []
    for p in labels:
        domain = p[0]
        label = p[1]
        node_list["id"].append(domain)
        node_list["label"].append(label)
        if label == "escort":
            escort.append(domain)
        if label == "forum":
            forum.append(domain)
    """
    node_frame = pd.DataFrame.from_dict(node_list)
    edge_frame = pd.DataFrame.from_dict(edge_list)
    G = nx.Graph()
    G = nx.from_pandas_edgelist(edge_frame, 'source', 'target')
    pos = nx.spring_layout(G)  # positions for all nodes
    edges = [(row['source'], row['target']) for index, row in edge_frame.iterrows()]
    #G.add_edges_from(edges)

    # options = {"edgecolors": "tab:gray", "node_size": 100, "alpha": 0.9}
    # nx.draw_networkx_nodes(G, pos, nodelist= list(unique_new_numbers), node_color="tab:blue", **options)
    # nx.draw_networkx_nodes(G, pos, nodelist= escort, node_color="tab:red", **options)
    # nx.draw_networkx_nodes(G, pos, nodelist= forum, node_color="tab:green", **options)
    #
    # nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    # nx.draw_networkx_edges(
    #     G,
    #     pos,
    #     edgelist=edges,
    #     width=8,
    #     alpha=0.5,
    #     edge_color="tab:grey",
    # )

    #figure(figsize=(10, 8))
    for node, data in G.nodes(data=True):
        data['group'] = labels[node]


    nw.visualize(G)
    #nx.draw(G, with_labels=True)
    #plt.show()
    #node_frame.to_csv("node_list.csv", index=False)
    #edge_frame.to_csv("edge_list.csv", index=False)
