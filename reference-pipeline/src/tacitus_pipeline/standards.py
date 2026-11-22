"""Standards vocabulary for source lineage and authored interpretation records."""
from .core import canonical, digest, validate


def standards_graph(data, ontology, layer):
    sources, entities, statements = validate(data, ontology)
    records = []
    for source in sources.values():
        records.append({'@id':'urn:tacitus:source:'+source['id']+':'+source['version'], '@type':'prov:Entity',
                        'prov:atLocation':{'@id':source['url']}, 'tacitus:sourceHash':source['version'],
                        'skos:prefLabel':source['title']})
    for identifier in layer['statement_ids']:
        statement = statements[identifier]
        passage_id = 'urn:tacitus:passage:'+identifier+':'+statement['source_version']
        records.append({'@id':passage_id,'@type':'prov:Entity','prov:value':statement['quote'],
                        'prov:wasDerivedFrom':{'@id':'urn:tacitus:source:'+statement['source_id']+':'+statement['source_version']},
                        'tacitus:codepointStart':statement['start'],'tacitus:codepointEnd':statement['end']})
        records.append({'@id':'urn:tacitus:interpretation:'+identifier,'@type':'prov:Entity',
                        'prov:wasDerivedFrom':{'@id':passage_id},'prov:value':statement['interpretation'],
                        'tacitus:reviewState':'proposed','tacitus:modality':statement['modality'],
                        'tacitus:qualifiers':canonical(statement['qualifiers'])})
    return {'@context':{'prov':'http://www.w3.org/ns/prov#','skos':'http://www.w3.org/2004/02/skos/core#',
                        'tacitus':'https://tacitus.me/ns/reference#'},'@graph':records,
            'tacitus:ontologyHash':digest(ontology),'tacitus:layerVersion':layer['version']}
