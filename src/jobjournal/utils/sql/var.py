class PositionsTable:
    # Define database variables' name for positions table
    _NAME ="positions"
    
    id = "id"
    date = "pub_date"
    title = "position"
    comp = "company"
    loc = "location"
    source = "source"
    interest = "hype"
    status = "status"
    salary = "salary"
    details = "details"
    skills = "skills"
    motivation = "motivation"
    timeline = "actions"

class ContactsTable:
    # Define database variables' name for contacts table
    _NAME = "contacts"
    
    id = "id"
    name = "name"
    comp = "company"
    mail = "mail"
    phone = "phone"

class PlacesTable:
    _NAME = "places"

    id = "id"
    place = "place"
    lat = "lat"
    lon = "long"

class JoinTable1:
    # Join table between positions and places
    _NAME = "position_places"

    id = "id"
    pos = "position"
    place = "place"