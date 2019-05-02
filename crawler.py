from bs4 import BeautifulSoup
import requests, re, graph

initial = "https://en.wikipedia.org/wiki/Spider-Man"
root = "Spider-Man"

print("starting")

def recurse(depth, link, mapping, node):
    if depth == 10:
        print("Hit Depth of 10")
        return
    r=requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')
    article = soup.find('div', attrs={"id":"bodyContent"})
    for link in article.findAll('a', attrs={'href':re.compile("^/wiki/")}):
        text = link.text
        if len(text.split(" ")) > 2:
            continue
        if mapping.does_vertex_exist(link.text):
            if mapping.does_edge_exist(node, link.text):
                continue

        mapping.add_vertex(link.text)
        mapping.add_edge(node, link.text)
        recurse(depth+1,"https://en.wikipedia.org" + link.get('href'), mapping, link.text)
        
mapping = graph.Graph()
mapping.add_vertex(root)
recurse(0, initial, mapping, root)

mst = graph.mst_krusal(mapping)

with open("output_commands.cipher", "w+") as f:
    f.write("CREATE (:Root {{ Text:\"{}\"}};\n".format(root))
    for v in mapping:
        f.write("CREATE (:Node {{ Text:\"{}\"}};\n".format(v))
    for v in mapping:
        for n in v.get_neighbours():
            f.write("""MATCH (a) (b)
            WHERE a.Text = "{}" AND b.Text = "{}" 
            MERGE (a) - [] - (b);\n""".format(v,n))

print("Finished!")