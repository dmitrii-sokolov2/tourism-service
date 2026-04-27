
from api.v1.routes.user_routes import (
    UserListResource, UserResource, UserBulkDeleteResource, UserBookTourResource
)
from api.v1.routes.destination_routes import (
    DestinationListResource, DestinationResource
)
from api.v1.routes.tour_routes import (
    TourListResource, TourResource, AvailableToursResource
)

__all__ = [
    'UserListResource', 'UserResource', 'UserBulkDeleteResource', 'UserBookTourResource',
    'DestinationListResource', 'DestinationResource',
    'TourListResource', 'TourResource', 'AvailableToursResource'
]