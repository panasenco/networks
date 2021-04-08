from collections import defaultdict
from difflib import SequenceMatcher

import ads
from nameparser import HumanName
from nameparser.config import CONSTANTS
import networkx as nx
from networkx.readwrite.gexf import write_gexf

CONSTANTS.titles.remove(*CONSTANTS.titles) # This data set of names contains no titles

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
        paper_authors = list(paper.author)
        if len(paper_authors) > 1:
            for second_author in paper_authors[1:]:
                solar_coauthorship.add_edge(paper_authors[0], second_author)
        else:
            solar_coauthorship.add_node(paper_authors[0])
    # Merge duplicate author names
authors = [(author, HumanName(author)) for author in solar_coauthorship.nodes]
lnfi = defaultdict(list) # Last name, first initial
for author, parsed in authors:
    if len(parsed.first) > 0:
        lnfi[parsed.last, parsed.first[0]].append((author, parsed))

for (last_name, first_initial), group in lnfi.items():
    # Filter non-initials only
    filtered_group = [(author, parsed) for author, parsed in group
                      if len(parsed.first.rstrip(".")) > 1]
    if len(filtered_group) >= 1:
        # Sort by descending degree
        sorted_group = sorted(
            filtered_group,
            key=lambda g: nx.degree(solar_coauthorship, g[0]),
            reverse=True,
        )
        first_name = sorted_group[0][1].first
        for alt_author, alt_parsed in sorted_group[1:]:
            if SequenceMatcher(None, first_name, alt_parsed.first).ratio() >= 0.8:
                alt_parsed.first = first_name
            else:
                print(f"Warning: Multiple first name candidates for last name "
                      f"{last_name} and first initial {first_initial}: {first_name} "
                      f"and {alt_parsed.first}")

    write_gexf(solar_coauthorship, "solar/solar_coauthorship.gexf.gz")
