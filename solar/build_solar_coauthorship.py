import ads
import networkx as nx
from networkx.readwrite.gexf import write_gexf

SOLAR_ASTROPHYSICS_QUERY = (
    'keyword:"Astrophysics - Solar and Stellar Astrophysics" '
    'title:("solar" OR "sun" OR "helio" OR "cme" OR "corona")'
    # 'year:2020-2021'
)

if __name__ == "__main__":
    # Make sure environment variable ADS_DEV_KEY is defined
    solar_papers = ads.SearchQuery(
        q=SOLAR_ASTROPHYSICS_QUERY,
        fl=["author"],
        max_pages=1000,
    )
    solar_coauthorship = nx.DiGraph()
    for paper in solar_papers:
        authors = list(paper.author)
        if len(authors) > 1:
            for second_author in authors[1:]:
                solar_coauthorship.add_edge(authors[0], second_author)
        else:
            solar_coauthorship.add_node(authors[0])
    write_gexf(solar_coauthorship, "solar/solar_coauthorship.gexf.gz")
