from schema import get_connection


# Check user's role
def check_role(username, required_role):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM users
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False

    if result[0] == required_role:
        return True

    return False