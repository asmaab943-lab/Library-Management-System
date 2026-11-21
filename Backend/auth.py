from data import users


# Check user's role
def check_role(username, required_role):

    if username not in users:
        return False

    if users[username]["role"] == required_role:
        return True

    return False