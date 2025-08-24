```markdown
# GitHub Following Fetcher

A simple Python script to fetch and save the complete list of GitHub users that a specified user is following.

## Features

- Retrieves the full list of users a GitHub account is following.
- Automatically handles pagination to fetch all users, even if the list is large.
- Saves the result in a simple text file (`following_users.txt`) with one username per line.
- Easy to customize and extend.

## Prerequisites

- Python 3.6 or newer.
- `requests` library (install via `pip install requests`).

## Usage

1. Clone or download this repository.

2. Open the script (`github_following_fetcher.py`) and modify the `username` variable to the GitHub username you want to fetch following users for:

   ```
   username = "target-github-username"
   ```

3. Run the script:

   ```
   python github_following_fetcher.py
   ```

4. The list of usernames the specified user is following will be saved to `following_users.txt` in the same directory.

## How It Works

The script queries GitHub’s REST API endpoint to get the list of followed users, handling up to 100 users per API request. It reads the pagination information from API response headers to fetch all pages until complete. If the API returns an error or rate limit is hit, the script stops.

## Notes

- The script currently makes **unauthenticated** API requests. This limits you to 60 API calls per hour.
- For larger user followings or frequent runs, you may want to modify the script to use a GitHub personal access token to increase rate limits.

## License

This project is licensed under the MIT License.

## Author

Yours truly

## Contributing

Feel free to submit pull requests, bug reports, or feature requests.
