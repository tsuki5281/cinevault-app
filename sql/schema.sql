-- Movie catalogue
CREATE TABLE movies (
    movie_id VARCHAR(10) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director TEXT NOT NULL,
    country TEXT NOT NULL,
    description TEXT NOT NULL
);

-- User accounts
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE
);

-- Movie genres
CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL UNIQUE
);

-- Movie actors
CREATE TABLE actors (
    actor_id INT AUTO_INCREMENT PRIMARY KEY,
    actor_name VARCHAR(255) NOT NULL UNIQUE
);

-- Link movies to their genres
CREATE TABLE movie_genres (
    movie_id VARCHAR(10) NOT NULL,
    genre_id INT NOT NULL,

    PRIMARY KEY (movie_id, genre_id),

    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Link movies to their actors
CREATE TABLE movie_actors (
    movie_id VARCHAR(10) NOT NULL,
    actor_id INT NOT NULL,

    PRIMARY KEY (movie_id, actor_id),

    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
);

-- User movie ratings
CREATE TABLE ratings (
    user_id INT NOT NULL,
    movie_id VARCHAR(10) NOT NULL,
    stars INT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, movie_id),

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),

    CONSTRAINT chk_rating_stars CHECK (stars BETWEEN 1 AND 5)
);

-- User movie watchlists
CREATE TABLE watchlist (
    user_id INT NOT NULL,
    movie_id VARCHAR(10) NOT NULL,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, movie_id),

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);