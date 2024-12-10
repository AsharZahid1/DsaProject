import streamlit as st

# File to store user credentials
DATABASE_FILE = "database.txt"

# Data structures for the social network
class User:
    def __init__(self, user_id, name, password):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.friends = []  # Adjacency list for friendships
        self.posts = []    # List of posts
        self.feed = []     # Stack for the user's newsfeed
        self.friend_requests = []  # Queue for friend requests
        self.notifications = []  # Stack for notifications

# Initialize the graph of users
class SocialNetwork:
    def __init__(self):
        self.users = {}  # User storage: {user_id: User}
        self.load_users()

    def load_users(self):
        """Load users from the database file."""
        try:
            with open(DATABASE_FILE, "r") as file:
                for line in file:
                    name, password = line.strip().split()
                    self.add_user(name, password, from_file=True)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(DATABASE_FILE, "w"):
                pass

    def save_user(self, name, password):
        """Save a new user to the database file."""
        with open(DATABASE_FILE, "a") as file:
            file.write(f"{name} {password}\n")

    def add_user(self, name, password, from_file=False):
        """Add a new user to the network."""
        user_id = len(self.users)
        self.users[user_id] = User(user_id, name, password)
        if not from_file:  # Avoid duplicate writing when loading from file
            self.save_user(name, password)

    def find_user_by_name(self, name):
        """Find a user by name."""
        for user in self.users.values():
            if user.name == name:
                return user
        return None

    def send_friend_request(self, from_user, to_user):
        """Send a friend request."""
        if from_user in to_user.friend_requests:
            st.warning(f"{to_user.name} has already received a request from {from_user.name}.")
            return
        to_user.friend_requests.append(from_user)
        to_user.notifications.append(f"{from_user.name} sent you a friend request.")
        st.success(f"Friend request sent to {to_user.name}.")

    def accept_friend_request(self, user, from_user):
        """Accept a friend request."""
        user.friend_requests.remove(from_user)
        user.friends.append(from_user)
        from_user.friends.append(user)
        st.success(f"You are now friends with {from_user.name}.")
        from_user.notifications.append(f"{user.name} accepted your friend request.")

    def create_post(self, user, content):
        """Create a new post."""
        post = {"content": content, "likes": 0, "dislikes": 0, "author": user.name}
        user.posts.append(post)
        for friend in user.friends:
            friend.feed.append(post)
            friend.notifications.append(f"{user.name} created a new post.")
        st.success("Post created successfully!")

# Instantiate the social network
network = SocialNetwork()

# Streamlit app interface
st.title("Social Network Simulation")

# Login/Sign-up section
st.sidebar.header("Login / Sign-up")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
choice = st.sidebar.radio("Choose an option:", ["Login", "Sign-up"])

current_user = None

if choice == "Sign-up":
    if st.sidebar.button("Create Account"):
        if network.find_user_by_name(username):
            st.sidebar.error("Username already exists.")
        else:
            network.add_user(username, password)
            st.sidebar.success("Account created! Please log in.")

elif choice == "Login":
    if st.sidebar.button("Login"):
        user = network.find_user_by_name(username)
        if user and user.password == password:
            current_user = user
            st.sidebar.success(f"Welcome, {current_user.name}!")
        else:
            st.sidebar.error("Invalid username or password.")

# Main interface
if current_user:
    st.header(f"Welcome, {current_user.name}")

    # Post creation
    st.subheader("Create a Post")
    post_content = st.text_area("What's on your mind?")
    if st.button("Post"):
        network.create_post(current_user, post_content)

    # View feed
    st.subheader("Your Feed")
    if current_user.feed:
        for post in reversed(current_user.feed):
            st.write(f"**{post['author']}**: {post['content']}")
            st.write(f"Likes: {post['likes']} | Dislikes: {post['dislikes']}")
    else:
        st.write("Your feed is empty.")

    # Friend requests
    st.subheader("Friend Requests")
    if current_user.friend_requests:
        for friend in current_user.friend_requests:
            if st.button(f"Accept request from {friend.name}"):
                network.accept_friend_request(current_user, friend)
    else:
        st.write("No friend requests.")

    # Notifications
    st.subheader("Notifications")
    if current_user.notifications:
        for notification in reversed(current_user.notifications):
            st.write(notification)
    else:
        st.write("No notifications.")

# Footer
st.sidebar.info("Developed as part of a Social Network Simulation Project.")
