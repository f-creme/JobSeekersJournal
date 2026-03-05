class PositionsTable:
    # Define database variables' name for positions table
    table_pos ="positions"
    
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
    table_con = "contacts"
    
    id = "id"
    name = "name"
    comp = "company"
    mail = "mail"
    phone = "phone"

class PlacesTable:
    table_places = "places"

    id = "id"
    place = "place"
    lat = "lat"
    lon = "long"

class JoinTable1:
    # Join table between positions and places
    join_pos_places = "position_places"

    id = "id"
    pos = "position"
    place = "place"