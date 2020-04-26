from app import Venue, db

db.session.add_all([
   Venue(name="The Musical Hop", city="San Francisco", state="CA",
      address="1015 Folsom Street", phone="123-123-1234", genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"], 
      facebook_link="https://www.facebook.com/TheMusicalHop", 
      image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"),
   Venue(name="The Dueling Pianos Bar", city="New York", state="NY",
      address="335 Delancey Street", phone="914-003-1132", genres=["Classical", "R&B", "Hip-Hop"], 
      facebook_link="https://www.facebook.com/theduelingpianos",
      image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"),
   Venue(name="Park Square Live Music & Coffee", city="San Francisco", state="CA",
      address="34 Whiskey Moore Ave", phone="415-000-1234", genres=["Rock n Roll", "Jazz", "Classical", "Folk"], 
      facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
      image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80")])

db.session.commit()