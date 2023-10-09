from enum import Enum
from collections import namedtuple
from typing import (
    Optional,
    Union,
    List
)

import pydantic


Edge = namedtuple('Edge', ['out', 'label', 'in_'])


class Interface(Enum):
    TRANSDUCTIVE = 'transductive'
    INDUCTIVE = 'inductive'


class Commands(Enum):
    '''
    This class is an enumeration of valid export commands.

    Args:
        PG - This request exports property-graph.
        RDF - This request exports RDF.
    '''

    PG = 'export-pg'
    RDF = 'export-rdf'


class Params(pydantic.BaseModel):
    '''
    Args:
        endpoint - your JanusGraph endpoint DNS name.
        clone_cluster - If set to true, the export process
                        clones your DB cluster, exports from the clone,
                        and then deletes the clone when it is finished.
    '''

    endpoint: str
    clone_cluster: bool = False
    user: str = ''
    password: str = ''


class BaseType(Enum):
    '''
    This class is an enumeration of Indicates the type of base target
    task.
    '''


class NodeType(BaseType):
    '''
    This class is an enumeration of Indicates the type of target
    task to be performed on the node.
    '''

    classification = 'classification'
    regression = 'regression'

class EdgeType(BaseType):
    '''
    This class is an enumeration of Indicates the type of target
    task to be performed on the edge.
    '''

    classification = 'classification'
    regression = 'regression'
    link_prediction = 'link_prediction'


class BaseTarget(pydantic.BaseModel):
    '''
    The targets field in a JSON training data export configuration
    contains an array of target objects that specify a training task
    and and the machine-learning class labels for training this task.

    Args:
        type: Indicates the type of target task to be performed on
              the node or edge.
        split_rate: An estimate of the proportions of nodes or edges
                    that the training, validation, and test stages will
                    use, respectively. These proportions are represented
                    by a JSON array of three numbers between zero and one
                    that add up to one.
    '''

    type: Union[NodeType, EdgeType] = NodeType('classification')
    split_rate: tuple[float, float, float] = (0.9, 0.1, 0.0)

    @pydantic.validator('split_rate')
    def split_rate_sum_must_eq_1(cls, split_rate):
        if any([x < 0 for x in split_rate]):
            raise ValueError('Split rate must be greater then zero')

        if sum(split_rate) != 1:
            raise ValueError('Split rate sum must equally 1')

        return split_rate


class PGTarget(BaseTarget):
    '''
    The property-graph label of a target node (vertex). A target
    object must contain a node element or an edge element, but not both.

    Args:
        node - The property-graph label of a target node (vertex).
        edge - The value of an edge field is a JSON array of three
               strings that represent the start-node's property-graph
               label(s), the property-graph label of the edge itself,
               and the end-node's property-graph label(s).
        property - Specifies a property of the target vertex or edge.
                   This field is required, except when the target
                   task is link prediction.
        separator - (Optional) Used with a classification task. The
                    separator field specifies a character used to
                    split a target property value into multiple
                    categorical values when it is used to store
                    multiple category values in a string.
    '''

    node: Optional[str] = None
    edge: Optional[Edge] = None
    property: str
    separator: Optional[pydantic.constr(min_length=1, max_length=1)] = None

    # @pydantic.root_validator(skip_on_failure=True)
    # def check_valid_type(cls, values):
    #     type = values.get('type')

    #     if not (values.get('node') is None) and not (values.get('edge') is None):
    #         raise ValueError(
    #             'A target object must contain a node element or an edge element, but not both.'
    #         )
    #     elif 'node' in values:
    #
    #         try:
    #             NodeType(type)

    #         except ValueError:
    #             raise ValueError(
    #                 f'"{type}" is not valid task. The supported task types for nodes are "classification" and "regression"'
    #             )

    #     elif 'edge' in values:
    #         try:
    #             EdgeType(type)

    #         except ValueError:
    #             raise ValueError(
    #                 f'"{type}" is not valid task. The supported task types for nodes are "classification", "regression" and "link_prediction"'
    #             )

    #     else:
    #         raise ValueError(
    #             'A target object must contain a node element or an edge element'
    #         )


class RDFTarget(BaseTarget):
    ...


class BaseFeature(pydantic.BaseModel):
    # TODO

    '''
    Args:
        node
        edge
        property
        type
        norm
        language
        max_length
        separator
        range
        bucket_cnt
        slide_window_size
        imputer
        max_features
        min_df
        ngram_range
        datetime_parts
    '''

    node: Optional[str] = None
    edge: Optional[Edge] = None
    property: Optional[str] = None
    type: str = 'category'


class PGFeature(BaseFeature):
    ...


class RDFFeature(BaseFeature):
    ...


class UserJob(pydantic.BaseModel):
    '''
    Args:
        name - Training data configuration name.
        targets - A class label targets that represent
                  the machine-learning class labels for
                  training purposes.

        features - A JSON array of node property features.
    '''

    name: str
    target: PGTarget
    features: Optional[List[PGFeature]]


class UtilJob(pydantic.BaseModel):
    name: str
    target: Optional[PGTarget]
    features: Optional[List[PGFeature]]
    entity_id: int
    interface: Optional[Interface] = Interface('transductive')
    n_layers: Optional[int]


class AdditionalParams(pydantic.BaseModel):
    '''Contains an array of training-data configuration objects'''

    jobs: List[Union[UtilJob, UserJob]]


class RequestBody(pydantic.BaseModel):
    '''
    This class describes a valid export request body.

    Args:
        command - This field provides a choice between
                  exporting property-graph and RDF.
        output_s3_path - This field contains the address
                         of the object storage to which
                         the data will be exported.
        params - object in an export request can contain various fields.
        additional_params - object contains fields that you
                            can use to specify machine-learning
                            class labels and features for training
                            purposes and guide the creation of
                            a training data configuration file.
    '''

    command: Commands = Commands.PG
    output_s3_path: str
    bucket: str
    params: Params
    additional_params: Optional[AdditionalParams]
