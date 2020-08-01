def add_post(conn, server_id: int, category_name: str, title: str, subtitle: str, content: str):
    curr = conn.cursor()
    curr.execute(
        "INSERT INTO smashcords2blog.post (serverid, catname, title, subtitle, content) VALUES (%s, %s, %s, %s, %s)",
        (server_id, category_name, title, subtitle, content))
    conn.commit()
    curr.close()


def get_server_posts(conn, server_id: int, category_name: str, title: str) -> list:
    curr = conn.cursor()
    curr.execute(
        "SELECT serverid, catname, title FROM smashcords2blog.post WHERE serverid = %s AND catname = %s AND title = %s",
        (server_id, category_name, title))
    result = curr.fetchall()
    curr.close()
    return result


def remove_post(conn, server_id: int, category_name: str, title: str):
    curr = conn.cursor()
    curr.execute("DELETE FROM smashcords2blog.post WHERE serverid = %s AND catname = %s",
                 (server_id, category_name))
    conn.commit()
    curr.close()
