import requests  # Import requests library to handle HTTP requests


def get_all_following_users(username):
    """
    Fetches the complete list of GitHub users that the specified user is following.

    This function handles pagination automatically by requesting multiple pages
    of results from the GitHub API until it has collected all users.

    Args:
        username (str): GitHub username to fetch following list for.

    Returns:
        list: A list of GitHub usernames that the user is following.
    """
    users = []  # List to store the usernames found
    per_page = 100  # Max number of users returned per API request (GitHub max limit)
    page = 1  # Start from the first page of results

    while True:
        # Construct the API URL with pagination parameters
        url = f"https://api.github.com/users/{username}/following?per_page={per_page}&page={page}"

        # Make a GET request to the GitHub API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: Status code {response.status_code}")
            break  # Stop if there's an error fetching this page

        # Parse the JSON response (list of users on this page)
        data = response.json()

        # If the response data is empty, we've fetched all pages
        if not data:
            break

        # Add the usernames from this page to the overall list
        users.extend(user['login'] for user in data)
        print(f"Fetched page {page} with {len(data)} users")

        # Inspect the 'Link' header to check if there is a next page
        link_header = response.headers.get('Link', '')

        # If 'rel="next"' not in link header, this is the last page
        if 'rel="next"' not in link_header:
            break  # No more pages to fetch

        page += 1  # Move to the next page

    return users  # Return the full list of followed usernames


if __name__ == "__main__":
    # Set the GitHub username to fetch following users for
    username = "mao1910"

    # Fetch the entire list of following users
    all_following = get_all_following_users(username)

    print(f"\nTotal users {username} is following: {len(all_following)}")

    # Save the list of usernames to a text file, one username per line
    with open("following_users.txt", "w") as file:
        for user in all_following:
            file.write(user + "\n")

    print("Usernames saved to following_users.txt")
