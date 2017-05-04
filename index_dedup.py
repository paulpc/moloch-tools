from elasticsearch import Elasticsearch, helpers
import json
from multiprocessing import Pool



def reindex_sessions(fuckup):
    """reindexes a messed up index into the apropriate one.
    Uses the state saved in session_map by the main program for the map between the goods and the bads indexes
    I was too lazy to do the multithreading right, so we're just taking in one parameter so I can use the Pool.map function"""
    try:
        # reading config, index map, and creating elasticsearch object
        mpbls=json.load(open('session_map.json'))
        conf = json.load(open('config.json'))
        prod_es=Elasticsearch(conf['hosts'])
        prod_es=Elasticsearch(hosts=conf["hosts"])
        # searching for all documents with the scroll methof
        page = prod_es.search(index=fuckup, scroll='2m', search_type='scan', size=1000)
        sid = page['_scroll_id']
        scroll_size = page['hits']['total']
        #every time we have a new pair, printing it to screen - we probably won't see it scrolling by
        print(fuckup, mpbls[fuckup])
        # Start scrolling through results
        while (scroll_size > 0):
            page = prod_es.scroll(scroll_id=sid, scroll='2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            # printing the scrolling status just so that we have something to scroll by
            print("[%s]scroll size: %d" %(mpbls[fuckup], scroll_size))         
            # preparing a list of documents based on this scroll batch by adding the operation and fixing the index name
            nw_hits=[]
            for hit in page['hits']['hits']:
                new_hit=hit
                new_hit.update({'_op_type': 'index', '_index': mpbls[fuckup]})
                nw_hits.append(new_hit)
            # bulk index based othe list created
            helpers.bulk(client=prod_es, actions=nw_hits, raise_on_error=False)
        # if everything went well thus far, it means the entire index was reindexed under the right name / mapping. 
        # Might as well delete it
        prod_es.indices.delete(fuckup)

    except:
        print('problems with',fuckup)
        # if it didn't work, oh well

if __name__ == "__main__":
    # reading configs
    conf = json.load(open('config.json'))
    prod_es=Elasticsearch(hosts=conf['hosts'])

    # getting a list of problematic uids - the ones where ElasticSearch relocated the lost shards into an index named by the UUID
    problem_uids=[]
    for indi in prod_es.cat.indices():
        if len(indi.keys()) > 3:
            ind=indi['index']
            try:
                uid=prod_es.indices.get(ind)[ind]['settings']['index']['uuid']
                if uid == ind:
                    problem_uids.append(uid)
            except:
                print("issues with %s" % ind)
    
    # mapping the problematic indices to the actual names they should have
    mappables={}
    for indi in prod_es.cat.indices():
        if len(indi.keys()) > 3:
            ind=indi['index']
            try:
                uid=prod_es.indices.get(ind)[ind]['settings']['index']['uuid']
                if uid in problem_uids and uid != ind:
                    mappables[uid]=ind
            except:
                print("issues with %s" % ind)
    # saving the results to file - will use this file for the mapping in the process pool
    json.dump(mappables, open('session_map.json','w'))
    # creating a multiprocessing pool of [pool] subprocesses
    p=Pool(conf['pool'])
    # paralell processing the indices (one per process)
    p.map(reindex_sessions, mappables.keys())
