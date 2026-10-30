import strawberry

from app.resolvers.country import Mutation, Query


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)