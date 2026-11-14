# CineVault Application Testing Checklist

This checklist is for teammates to try the CineVault Streamlit application and report any issues. It focuses on the main user-facing features rather than code-level or performance testing.

## Before You Start

1. Follow the setup instructions in the repository's `README.md`.
2. Start the application from the repository root:

   ```powershell
   streamlit run app.py
   ```

3. Use your own newly registered account for tests that create, edit or delete ratings and reviews. Each developer has a separate local database, so an account created on another developer's computer (including `OfficialAdmin1`) will not automatically exist in your database.
4. You can also sign in using one of the available demo profiles to explore pre-populated activity. Demo-profile ratings and reviews may vary depending on the local setup and previous testing. Avoid changing or deleting demo records unless you are deliberately testing those actions.

## How to Record Results

For each test, mark one status:

- **Pass** – the feature behaved as expected.
- **Fail** – the feature did not behave as expected.
- **Blocked** – the test could not be completed, for example because a database or setup dependency was unavailable.
- **Not tested** – the test has not been attempted.

If a test fails, note what you clicked, what you expected, what actually happened, and attach a screenshot where useful.

## Application Test Scenarios

### 1. Login and Registration

| ID | What to try | Expected result | Status / notes |
|---|---|---|---|
| APP-01 | Register a new account with a valid username and password, then confirm the password. | The account is created and you are signed in. | Not tested |
| APP-02 | Try registering with mismatched passwords or invalid input. | Registration is rejected and a helpful message is displayed. | Not tested |
| APP-03 | Sign out, then sign in with the account you created. Also try an incorrect password. | Valid credentials allow access; incorrect credentials are rejected. | Not tested |
| APP-04 | Sign in using an available demo profile, then sign out. | The selected demo profile opens and sign-out returns to the login screen. | Not tested |

### 2. Home Page

| ID | What to try | Expected result | Status / notes |
|---|---|---|---|
| APP-05 | Open Home and inspect the Featured Movie, Highest-Rated Movies and Most-Reviewed Movies sections. | The sections load with movie information and available community statistics. | Not tested |
| APP-06 | Select one or more genres under Explore by Genre, then choose Explore Selected Genres. | The Search page opens with the selected genres applied. | Not tested |
| APP-07 | Open a movie from one of the Home sections. | The correct Movie Details page opens. | Not tested |

### 3. Search and Movie Catalogue

| ID | What to try | Expected result | Status / notes |
|---|---|---|---|
| APP-08 | Enter at least two characters in Universal Search. Try a movie title, actor name and genre. | Relevant suggestions appear in the Movies, Actors and Genres columns where matches exist. | Not tested |
| APP-09 | Select a suggested actor or genre, and try selecting more than one. | The selection is reflected in the search filters and can be removed. | Not tested |
| APP-10 | Search using a keyword and/or selected filters. Try Genre Matching and Actor Matching with Any and All. | Results match the selected search criteria. | Not tested |
| APP-11 | Change Sort results between Title A–Z and Highest rated. | Results are displayed in the selected order. | Not tested |
| APP-12 | Use Clear Filters, then try Load More Movies on recommendations or search results. | Filters are reset; Load More displays additional results when more are available. | Not tested |
| APP-13 | Submit a search with no keyword and no selected filters, and try a search with no matching results. | The app prompts for a search input or displays a clear no-results message. | Not tested |

### 4. Movie Details, Ratings and Reviews

| ID | What to try | Expected result | Status / notes |
|---|---|---|---|
| APP-14 | Open a movie and inspect its title, description, director, country, genres, cast and community rating. | The details correspond to the selected movie. Movies without ratings show an appropriate not-rated message. | Not tested |
| APP-15 | Add a movie to the watchlist using the bookmark icon, then remove it. | The bookmark state changes and the movie is added to or removed from the watchlist. | Not tested |
| APP-16 | Submit a star rating, change it, and remove it. | The saved rating updates correctly and can be removed. | Not tested |
| APP-17 | Submit a review with tags and, optionally, the spoiler checkbox selected. Then edit and delete your review. | The review is saved, displayed with its tags/spoiler status, can be edited and can be deleted. | Not tested |
| APP-18 | In Community Reviews, toggle Hide spoiler reviews and change sorting between Newest first, Oldest first and Highest rated. | The displayed reviews follow the selected spoiler setting and sort order. Reviewer names and available star ratings are shown. | Not tested |

### 5. My Activity and Navigation

| ID | What to try | Expected result | Status / notes |
|---|---|---|---|
| APP-19 | Open My Activity and inspect the Ratings, Reviews, Watched and Watchlist summary counts. | The counts reflect the signed-in user's activity. | Not tested |
| APP-20 | Check My Contributions, Watched History and My Watchlist. Open a movie from each section where available. | The relevant records are displayed and View Movie opens the correct movie. | Not tested |
| APP-21 | Remove a movie from Watched History and remove a movie from My Watchlist. | The selected entries disappear from the corresponding lists and the counts update. | Not tested |
| APP-22 | Submit a review for a movie, then return to My Activity. Navigate between Home, Search, Movie Details and My Activity, and sign out/in again. | The reviewed movie appears in Watched History, navigation returns to the expected page, and saved activity remains after signing in again. | Not tested |

## Issue Reporting

For any failed or blocked test, copy the details below into your feedback:

- **Test ID:**
- **Browser / operating system:**
- **Steps taken:**
- **Expected result:**
- **Actual result / error message:**
- **Screenshot (if available):**

Please report issues with the Test ID so they can be traced back to the relevant feature.

## Scope Note

This checklist is for manual testing of the Streamlit application. Automated test coverage is documented in `docs/streamlit_testing.md`, while performance measurements and analysis are documented in `docs/performance_analysis.md`.
