# CineVault Streamlit Implementation

## 1. Overview

CineVault is a movie discovery and community-review application built with Streamlit. It allows members to explore a movie catalogue, discover movies through search and recommendations, view community ratings and reviews, and manage their own movie activity.

The Streamlit application provides the user interface and coordinates requests between the frontend screens and the existing backend modules. Movie catalogue information, account information, ratings, watchlist records and watched history are retrieved through the MariaDB-related modules, while community review documents are retrieved through the MongoDB-related module. The application brings together the information required by each screen without requiring users to interact directly with either database.

This document describes the organisation and behaviour of the Streamlit application. Detailed backend function descriptions and database operations are maintained separately in:

- `docs/catalogue_api.md`
- `docs/ratings_watchlist_api.md`
- `docs/reviews_api.md`

## 2. Application Structure and Navigation

The application is organised into separate screens, database modules and reusable UI components. This keeps the presentation layer separate from database operations and allows common interface elements to be reused across screens.

### 2.1 Main Navigation

After signing in, members can navigate between the main areas of CineVault:

| Page | Purpose |
|---|---|
| **Home** | Introduces the movie community and highlights movies and community activity. |
| **Search** | Allows members to discover movies using keywords, actors, genres and sorting options. |
| **Movie Details** | Opens the selected movie's information, rating controls and community reviews. This page is reached from movie selections in the application. |
| **My Activity** | Shows the signed-in member's ratings, reviews, watchlist and watched history. |

The application uses Streamlit session state to retain information needed across interactions and page reruns. This includes the current member, selected page, selected movie, previous page, active search filters and loaded search results. When a member opens a movie from Search or Home, the selected movie and source page are retained so that the application can display the correct details and provide a return path.

### 2.2 Application Styling

The interface uses shared styling and reusable UI components to maintain a consistent CineVault appearance. Branding elements, headings, movie cards, rating indicators and review cards are presented consistently across the application. The layout uses Streamlit components such as columns, containers, forms, tabs, buttons and expanders to organise information and user interactions.

## 3. User Authentication

CineVault provides account access through the login screen. Members can sign in using their account credentials or create a new account through the registration form. Demo profiles are also available for users who want to explore the application without creating a separate account.

The authentication flow includes input checks before submitting credentials, password confirmation during registration, and feedback when credentials are invalid or an account cannot be created. After successful authentication, the member's account information is stored in session state and used to retrieve member-specific information throughout the application.

The signed-in member's identity is displayed in the navigation area. Signing out clears the active session state and returns the application to the login screen.

## 4. Home and Movie Discovery

The Home page acts as the starting point for movie discovery. It highlights movies and activity from the CineVault community so that members can begin browsing without first entering a search query.

Depending on the available catalogue and community data, the Home page presents discovery content such as:

- **Featured movie content:** a selected movie spotlight that introduces a movie and provides a path to its details.
- **Highest-rated movies:** movies ranked using submitted member ratings, with the average rating and number of ratings displayed.
- **Most-reviewed movies:** movies receiving the most written community reviews, with review activity summarised.
- **Popular review tags:** frequently used tags that provide an overview of topics and themes appearing in community reviews.
- **Genre and actor discovery:** shortcuts that help members explore movies through genres and selected actors.

Selecting a movie from a discovery section opens its Movie Details page. The Home page therefore acts as both an overview of community activity and an entry point into the movie catalogue.

## 5. Movie Search and Catalogue

The Search page provides a more targeted way to find movies. Members can search using a movie title, actor name or genre, and can combine search terms with additional catalogue filters.

### 5.1 Universal Search and Suggestions

The universal search field accepts a keyword and displays matching suggestions for movies, actors and genres. Suggestions allow members to move directly to a movie or add an actor or genre to the active search filters. This reduces the need to know the exact movie title before exploring the catalogue.

### 5.2 Genre and Actor Filters

Members can select one or more genres and actors to narrow the catalogue results. The interface provides selectable genre options and actor recommendations, as well as a way to review and remove selected filters.

When multiple genres or actors are selected, members can choose how the filters are matched:

- **Any:** a movie can match at least one of the selected genres or actors.
- **All:** a movie must match all selected genres or actors.

The title keyword, selected genres and selected actors can be combined in one search. The application also checks that at least one search term or filter has been provided before submitting a catalogue search.

### 5.3 Sorting and Search Results

Search results can be sorted alphabetically by title or by highest community rating. Movie cards display key information such as the movie title, genres, average community rating and rating count. Movies without submitted ratings are identified separately so that an unrated movie is not presented as having a zero-star rating.

The catalogue uses incremental loading rather than displaying every matching movie at once. Results are loaded in batches, and members can select **Load More Movies** to display the next batch. The active filters and loaded results are retained in session state so that the search can continue without requiring members to re-enter their selections.

For highest-rated sorting, the application ranks the complete set of movies matching the active filters before displaying the results in batches. This keeps the overall rating order consistent when additional results are loaded, rather than ranking each page independently.

### 5.4 Curated Movie Recommendations

When no search has been submitted, the Search page can display a curated set of community-relevant movies. This selection combines highly rated and frequently reviewed movies, while avoiding duplicate movie entries. Members can browse the recommendations and load additional results progressively.

## 6. Movie Details and Member Interactions

The Movie Details page presents the information and community activity associated with one selected movie. It includes the movie title, country, genres, catalogue identifier, description, director and cast where these details are available.

### 6.1 Community Rating

The page displays the movie's average community rating and the number of member ratings contributing to it. Rating indicators provide a quick visual representation of the movie's reception. Where no member ratings exist, the page identifies the movie as not yet rated.

Members can submit a star rating for a movie. An existing rating can be updated or removed. The interface checks whether the member has already rated the selected movie and provides the appropriate action.

### 6.2 Watchlist

Members can add a movie to their personal watchlist or remove it if it has already been saved. The watchlist state is reflected in the movie details interface, allowing members to identify whether the movie is currently in their list.

### 6.3 Writing and Managing Reviews

Members can submit a written review for a movie, add review tags and indicate whether the review contains spoilers. Existing reviews can be edited or deleted. The review form is presented alongside the member's rating controls so that both types of feedback can be managed from the movie details screen.

After a review is successfully saved, the application also attempts to record the movie in the member's watched history. This connects review activity with the member's viewing activity.

### 6.4 Community Review Display

The Community Reviews section displays reviews submitted by other members. Each review can include the reviewer's name, written feedback, tags, spoiler indication, submission date and associated star rating when available.

Members can choose to hide spoiler reviews and sort the community reviews using the available options:

- **Newest first**
- **Oldest first**
- **Highest rated**

Review content and reviewer ratings originate from separate database systems. The application combines the returned information for display so that a review can be shown together with its author's rating for the same movie. When a reviewer has not submitted a star rating, the interface indicates that no rating is available.

## 7. My Activity

The My Activity page provides a consolidated view of the signed-in member's personal activity in CineVault. It brings together four categories:

| Activity | Information available |
|---|---|
| **My Ratings** | Movies rated by the member and the corresponding star ratings. Members can manage their submitted ratings. |
| **My Reviews** | Reviews written by the member, including review text, spoiler status and tags. Members can view, edit and delete their reviews. |
| **My Watchlist** | Movies saved by the member for future viewing. Members can remove movies from the list. |
| **Watched History** | Movies recorded as watched by the member. Members can review their watched movies and manage their watched status. |

The page retrieves activity for the currently signed-in member, rather than displaying activity from other accounts. This gives each member one place to review and manage their contributions and saved movie lists.

## 8. Database Integration

The Streamlit layer calls the existing backend modules to retrieve and update application data. The database modules remain responsible for their respective database operations, while the Streamlit screens organise the returned information for display and handle user interactions.

### 8.1 MariaDB Integration

MariaDB is used for structured application data, including member accounts, movie catalogue information, genres, actors, ratings, watchlist records and watched history. The Streamlit screens use the relevant database functions to authenticate members, retrieve movie information, display rating summaries and manage member activity.

### 8.2 MongoDB Integration

MongoDB is used for community review documents and review-related information such as review text, spoiler status and tags. The Streamlit application retrieves review information for the selected movie, displays member reviews and supports review submission, editing and deletion.

### 8.3 Combining Information Across Databases

Some screens require information stored in both databases. For example, the Community Reviews section displays MongoDB review documents together with the corresponding member star ratings stored in MariaDB. Similarly, movie cards combine catalogue details with community rating summaries and, where applicable, review counts.

The Streamlit layer coordinates these results so that related information can be presented together. The detailed function signatures, validation rules and database implementation remain documented in the respective API Markdown files.

## 9. Application File Structure

The application is organised into the following main areas. File responsibilities are summarised at a high level; detailed backend APIs are documented separately.

| File or folder | Responsibility |
|---|---|
| `app.py` | Streamlit application entry point and navigation between screens. |
| `screens/login.py` | Login, account registration and demo-profile access. |
| `screens/home.py` | Homepage content and movie-discovery sections. |
| `screens/search.py` | Universal search, suggestions, filters, sorting, movie cards and incremental result loading. |
| `screens/movie_details.py` | Selected movie information, rating and review interactions, watchlist controls and community reviews. |
| `screens/activity.py` | Member ratings, reviews, watchlist and watched-history views. |
| `db/authentication.py` | Account authentication and member-related operations. |
| `db/catalogue.py` | Movie catalogue retrieval, search and filtering operations. |
| `db/home.py` | Data retrieval used by the Home page. |
| `db/activity.py` | Data retrieval for member activity. |
| `db/mariadb.py` | MariaDB operations for structured data and member activity. |
| `db/mongodb.py` | MongoDB operations for community review data. |
| `ui/styles.py` | Shared application styling. |
| `ui/components.py` | Reusable interface components. |
| `ui/review_card.py` | Review form and review-card interface. |

## 10. Summary

The Streamlit application brings CineVault's movie catalogue and community features together in one interface. Members can sign in or create an account, discover movies through the Home and Search pages, view movie details, submit ratings and reviews, manage their watchlist, and keep track of their watched history.

The frontend interacts with the existing MariaDB and MongoDB modules to retrieve and update information. By separating screens, database operations and reusable UI components, the application provides a structured interface while keeping the backend implementation details within their respective modules and API documentation.
