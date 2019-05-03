from bs4 import BeautifulSoup
import requests, re, graph

initial = "https://marvel.fandom.com/wiki/Peter_Parker_(Earth-616)"
root = "Spider-Man"

print("starting")

def recurse(depth, link, mapping, node):
    if depth == 4:
        print("on way up")
        return
    r=requests.get(link)
    soup = BeautifulSoup(r.text, 'html.parser')
    article = soup.find('div', attrs={"id":"mw-content-text"})
    print('found {} associations'.format(len(article)))
    for link in article.findAll('a', attrs={'href':re.compile("^/wiki/")}):
        text = link.text
        if text == "":
            continue
        if str.isdigit(text):
            continue
        if len(text.split(" ")) > 2:
            continue
        if mapping.does_vertex_exist(link.text):
            continue

        mapping.add_vertex(link.text)
        if not mapping.does_edge_exist(node, link.text):
            mapping.add_edge(node, link.text)
            recurse(depth+1,"https://en.wikipedia.org" + link.get('href'), mapping, link.text)
        
mapping = graph.Graph()
mapping.add_vertex(root)
recurse(0, initial, mapping, root)

with open("output_commands.cipher", "w+") as f:
    f.write("CREATE (:Root {{ Text:\"{}\"}});\n".format(root))
    for v in mapping:
        try:
            f.write("CREATE (:Node {{ Text:\"{}\"}});\n".format(v.get_key()))
        except:
            pass
    for v in mapping:
        for n in v.get_neighbours():
            try:
                f.write("MATCH (a) (b) WHERE a.Text = \"{}\" AND b.Text = \"{}\" MERGE (a) - [] - (b);\n""".format(v.get_key(), n.get_key()))    
            except:
                pass
            

print("Finished!")