from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # allow all origins for this exercise

# In-memory posts list
posts = [
    {"id": 1, "title": "First post", "content": "Hello world"},
    {"id": 2, "title": "Second post", "content": "More content"},
    {"id": 3, "title": "Another post", "content": "Some different content"},
    {"id": 4, "title": "Zebra post", "content": "Comes last when sorted by title"},
]


@app.route("/api/posts", methods=["GET"])
def list_posts():
    sort = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    # If no sort is provided, behave like the original list endpoint
    if not sort:
        return jsonify(posts), 200

    # Validate sort field
    if sort not in ("title", "content"):
        return jsonify({"error": "Invalid sort field"}), 400

    # Validate direction
    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid sort direction"}), 400

    reverse = direction == "desc"

    # Use sorted() so original 'posts' list order is preserved
    sorted_posts = sorted(posts, key=lambda p: p[sort], reverse=reverse)

    return jsonify(sorted_posts), 200

@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json()

    # Body must be JSON
    if data is None:
        return jsonify({"message": "Request body must be JSON"}), 400

    missing_fields = []
    if not data.get("title"):
        missing_fields.append("title")
    if not data.get("content"):
        missing_fields.append("content")

    if missing_fields:
        return jsonify(
            {"message": f"Missing required fields: {', '.join(missing_fields)}"}
        ), 400

    # Generate new unique integer id
    new_id = max((p["id"] for p in posts), default=0) + 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
    }

    posts.append(new_post)
    return jsonify(new_post), 201

@app.route("/api/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    # Find post with given id
    post = next((p for p in posts if p["id"] == id), None)
    if post is None:
        return jsonify({"message": f"Post with id {id} was not found."}), 404

    # Remove it
    posts.remove(post)
    return jsonify(
        {"message": f"Post with id {id} has been deleted successfully."}
    ), 200

@app.route("/api/posts/<int:id>", methods=["PUT"])
def update_post(id):
    # Find the post with the given id
    post = next((p for p in posts if p["id"] == id), None)
    if post is None:
        return jsonify({"message": f"Post with id {id} was not found."}), 404

    data = request.get_json() or {}

    # Update only provided fields, keep others
    if "title" in data:
        post["title"] = data["title"]
    if "content" in data:
        post["content"] = data["content"]

    # Respond with the updated post
    return jsonify(
        {
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
        }
    ), 200

@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    title_q = request.args.get("title", "").lower()
    content_q = request.args.get("content", "").lower()

    def matches(post):
        ok_title = True
        ok_content = True

        if title_q:
            ok_title = title_q in post.get("title", "").lower()
        if content_q:
            ok_content = content_q in post.get("content", "").lower()

        return ok_title and ok_content

    results = [p for p in posts if matches(p)]
    return jsonify(results), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
