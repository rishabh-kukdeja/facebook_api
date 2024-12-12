import requests
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/detect_fraud_profile', methods=['POST'])
def detect_fb():
    data = request.get_json()
    username = data.get('username')  # Extract 'username' from the JSON payload
    if not username:
        return jsonify({'error': 'Username is required.'}), 400
    
    base_url = "https://www.facebook.com/"
    url = base_url + username

    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)

    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)

    profile_info = user_profile_information(url, username)  
    post_info = fetch_user_posts(url, username)  
    data = {
        "profile_info": profile_info,
        "post_info": post_info
    }
    data_path = os.path.join(profile_dir, "data.json")
    # Save the data to data.json
    with open(data_path, "w") as data_file:
        json.dump(data, data_file, indent=4)
    return jsonify({'result': f"Data for '{url}' has been successfully processed."})


def user_profile_information(url, username):
    """
    Fetches the profile information from the given Facebook page URL
    and saves the selected details into a JSON file.
    """
    # Setup directories
    base_dir = os.path.join(os.getcwd(), username)
    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)

    # API endpoint and headers
    api_url = "https://facebook-pages-scraper2.p.rapidapi.com/get_facebook_pages_details"
    querystring = {"link": url}
    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
        "x-rapidapi-host": "facebook-pages-scraper2.p.rapidapi.com"
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=querystring)
    profile_info = {}
    if response.status_code == 200:
        data = response.json()[0]  # Extract the first item if the response is a list
        profile_info = {
            "SocialMediaPlatform": "Facebook",
            "Bio": ((data.get("bio") or "") + 
                    (data.get("about_me_text_content") or "") + 
                    (data.get("description") or "")),
            "Followers": data.get("followers_count"),
            "AccountPrivacy": data.get("status"),
            "creation_date": data.get("creation_date"),
            "user_id": data.get("user_id"),
            "Name": data.get("about_me_text"),
            "Username": username
        }
    return profile_info


def fetch_user_posts(page_url, username):
    """
    Fetch the latest posts from a Facebook page and save them as JSON.
    """
    api_url = "https://facebook-pages-scraper2.p.rapidapi.com/get_facebook_posts_details"
    querystring = {"link": page_url, "timezone": "UTC"}
    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
        "x-rapidapi-host": "facebook-pages-scraper2.p.rapidapi.com"
    }

    response = requests.get(api_url, headers=headers, params=querystring)
    post_details = []
    if response.status_code == 200:
        data = response.json().get("data", {}).get("posts", [])
        for post in data[:3]:  # Limit to 3 posts
            post_details.append({
                "Caption": post.get("values", {}).get("text", "No caption available")
            })
    return post_details


if __name__ == "__main__":
    app.run(debug=True)
