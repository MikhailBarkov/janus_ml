# import json
# import requests

# JANUS_GRAPH_ENDPOINT_URL = "ws://janusgraph:8182/gremlin"
# S3_ENDPOINT_URL = "http://s3:9000"
# EXPORT_SERVICE_URL = "http://localhost:8081/export"
# PROCESSING_SERVICE_URL = "http://localhost:8082/processing"
# TRAIN_SERVICE_URL = "http://localhost:8083/modeltraining"
# ENDPOINT_SERVICE_URL = "http://localhost:8084/call"

# # news_train = {
# #     "s3_params": {
# #       "bucket": "test-bucket",
# #       "s3_endpoint_url": S3_ENDPOINT_URL
# #     },
# #     "train_config_s3_key": "janusgraph_ml/news_job/train_config.json",
# #     "processing_config_s3_key": "janusgraph_ml/news_processed/processing_config.json"
# # }

# news_train = {
#     "s3_params": {
#       "bucket": "test-bucket",
#       "s3_endpoint_url": S3_ENDPOINT_URL
#     },
#     "train_config_s3_key": "janusgraph_ml/news_job/train_config.json",
#     "processing_config_s3_key": "janusgraph_ml/news_processed/processing_config.json"
# }

# requests.post(
#     TRAIN_SERVICE_URL, data=json.dumps(news_train)
# )

import gremlin_python
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import TraversalStrategy
from gremlin_python.process.strategies import LambdaRestrictionStrategy
from gremlin_python.process.graph_traversal import GraphTraversalSource, GraphTraversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P
from gremlin_python.statics import long

g = traversal().with_remote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))

# edges = g.E().hasLabel("link").count().next()
# node = g.V().hasLabel("news").next(10)
node = (
    g.call("predict")
    .with_("endpoint_id", "news_job")
    .with_("predict_entity_idx", "327692288")
    .with_("interface", "inductive")
    .next()
)

print(node)

# text = 'Syria attack symptoms consistent with nerve agent use WHO,"Wed 05 Apr 2017 Syria attack symptoms consistent with nerve agent use WHO. Victims of a suspected chemical attack in Syria appeared to show symptoms consistent with reaction to a nerve agent the World Health Organization said on Wednesday. ""Some cases appear to show additional signs consistent with exposure to organophosphorus chemicals a category of chemicals that includes nerve agents"" WHO said in a statement putting the death toll at at least 70. The United States has said the deaths were caused by sarin nerve gas dropped by Syrian aircraft. Russia has said it believes poison gas had leaked from a rebel chemical weapons depot struck by Syrian bombs. Sarin is an organophosporus compound and a nerve agent. Chlorine and mustard gas which are also believed to have been used in the past in Syria are not. A Russian Defence Ministry spokesman did not say what agent was used in the attack but said the rebels had used the same chemical weapons in Aleppo last year. The WHO said it was likely that some kind of chemical was used in the attack because sufferers had no apparent external injuries and died from a rapid onset of similar symptoms including acute respiratory distress. It said its experts in Turkey were giving guidance to overwhelmed health workers in Idlib on the diagnosis and treatment of patients and medicines such as Atropine an antidote for some types of chemical exposure and steroids for symptomatic treatment had been sent. A U.N. Commission of Inquiry into human rights in Syria has previously said forces loyal to Syrian President Bashar al-Assad have used lethal chlorine gas on multiple occasions. Hundreds of civilians died in a sarin gas attack in Ghouta on the outskirts of Damascus in August 2013. Assads government has always denied responsibility for that attack. Syria agreed to destroy its chemical weapons in 2013 under a deal brokered by Moscow and Washington. But Russia a Syrian ally and China have repeatedly vetoed any United Nations move to sanction Assad or refer the situation in Syria to the International Criminal Court. ""These types of weapons are banned by international law because they represent an intolerable barbarism"" Peter Salama Executive Director of the WHO Health Emergencies Programme said in the WHO statement. - REUTERS"'
# source = 'nna'
# date = '4/5/2017'
# location = 'idlib'


# source = (
#     g.addV("news")
#         .property("text", text)
#         .property("source", source)
#         .property("date", date)
#         .property("location", location)
#         .next()
# )
# print(source)
# nodes = (
#     g.V(source).as_("a")
#         .V().hasLabel("news").as_("b")
#         .or_(
#             __.where("a", P.eq("b")).by("source"),
#             __.where("a", P.eq("b")).by("date"),
#             __.where("a", P.eq("b")).by("location")
#         )
#         .V(long(source.id)).addE("link").to("b")
#         .iterate()
# )
# print(nodes)
# trav = g
# for node in nodes:
#     trav = trav.V(source).addE('link').to(__.V(node))
#     trav = trav.V(node).addE('link').to(__.V(source))
# print('!!!')
# edges = trav.iterate()

# edges = (
# )
# node1 = g.V(491811048).next()
# node2 = g.V(491839720).next()
# edges = g.V(491811048).addE('link').to(__.V(491839720)).iterate()


# import dgl
# import torch
# from pytorch_lightning import LightningDataModule


# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# class DataModule(LightningDataModule):

#     def __init__(
#         self, graph, train_idx, val_idx, fanouts, batch_size
#     ):
#         super().__init__()

#         sampler = dgl.dataloading.NeighborSampler(
#             fanouts, prefetch_node_feats=["feat"], prefetch_labels=["label"]
#         )

#         self.graph = graph
#         self.train_idx = train_idx
#         self.val_idx = val_idx
#         self.sampler = sampler
#         self.batch_size = batch_size
#         self.in_feats = graph.ndata["feat"].shape[1]
#         self.n_classes = len(torch.unique(graph.ndata['label']))

#     def train_dataloader(self):
#         loader = dgl.dataloading.DataLoader(
#             self.graph,
#             self.val_idx,
#             self.sampler,
#             device=device,
#             batch_size=self.batch_size,
#             num_workers=2
#         )

#         with loader.enable_cpu_affinity():
#             return loader

#     def val_dataloader(self):
#         loader = dgl.dataloading.DataLoader(
#             self.graph,
#             self.val_idx,
#             self.sampler,
#             device=device,
#             batch_size=self.batch_size,
#             num_workers=2
#         )

#         with loader.enable_cpu_affinity():
#             return loader



# graph = dgl.data.CoraGraphDataset()[0]

# data_loader = dgl.dataloading.DataLoader(
#     graph,
#     torch.arange(graph.number_of_nodes()).to(device),
#     dgl.dataloading.MultiLayerFullNeighborSampler(2),
#     device=device,
#     batch_size=512,
#     num_workers=2
# )

# for input_nodes, output_nodes, blocks in data_loader:
#     block = blocks[0]
#     print(
#         'input', input_nodes,
#         'output', output_nodes,
#         'blocks', blocks,
#         'block', block,
#         'ndata', block.ndata,
#         'edata', block.edata
#      )
    # break



# import asyncio
# import aioboto3

# import json
# import io


# class S3Client:

#     def __init__(self, s3_endpoint_url: str):
#         self.session = aioboto3.Session()
#         self.s3_endpoint_url = s3_endpoint_url

#     def __call__(self):
#         return self.session.client(
#             service_name='s3',
#             endpoint_url=self.s3_endpoint_url,
#             aws_access_key_id='123',
#             aws_secret_access_key='12345678'
#         )



# async def f():
#     s3_client = S3Client('http://localhost:9000')
#     async with s3_client() as s3:
#         s3_obj = await s3.get_object(
#             Bucket="util-bucket",
#             Key='janusgraph_ml/test_name/edges_paper_citation_paper.csv'
#         )

#         batches = []
#         chunk_size = 32768
#         stream = s3_obj["Body"]

#         while txt := await stream.read(chunk_size):
#             batches.append(txt)

#         text = b''.join(batches)

#         print(s3_obj['ContentLength'], text)


# asyncio.run(f())